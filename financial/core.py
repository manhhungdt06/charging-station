import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import math

@dataclass
class LoanTerms:
    principal: float
    annual_rate: float
    term_months: int
    start_date: datetime

@dataclass
class ElectricityPricing:
    off_peak: float = 1500
    normal: float = 3200
    peak: float = 5200
    vinfast_rate: float = 4200
    vinfast_subsidy: float = 750

@dataclass
class OperatingCosts:
    land_lease_per_m2: float
    staff: float
    maintenance: float
    other: float

@dataclass
class ChargerConfig:
    type_name: str
    quantity: int
    power: float
    price: float

class ChargingStationFinancials:
    def __init__(self, config_path: str = "vinfast-charger.json"):
        self.charger_configs = self._load_charger_configs(config_path)
        self.electricity_pricing = ElectricityPricing()

    def _load_charger_configs(self, config_path: str) -> Dict:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return {c['name']: c for c in json.load(f)}
        except FileNotFoundError:
            raise FileNotFoundError(f"Charger config file not found: {config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in config file: {config_path}")

    def calculate_loan_payments(self, loan: LoanTerms) -> Dict:
        monthly_rate = loan.annual_rate / 12
        payment = loan.principal * (monthly_rate * (1 + monthly_rate)**loan.term_months) / ((1 + monthly_rate)**loan.term_months - 1)
        schedule = []
        remaining = loan.principal
        for month in range(loan.term_months):
            interest = remaining * monthly_rate
            principal = payment - interest
            remaining -= principal
            schedule.append({
                'month': month + 1,
                'payment': payment,
                'principal': principal,
                'interest': interest,
                'remaining': max(0, remaining)
            })
        return {
            'monthly_payment': payment,
            'total_interest': sum(m['interest'] for m in schedule),
            'schedule': schedule
        }

    def calculate_required_area(self, charger_configs: List[ChargerConfig], mounting_type: str) -> float:
        spot_length = 5.4
        spot_width = 2.5
        total_spots = sum(config.quantity for config in charger_configs)
        if mounting_type == "wall":
            width = spot_width * total_spots
            length = spot_length
            area = width * length
        elif mounting_type == "side":
            charger_spacing = 0.9
            width = (spot_width * total_spots) + (charger_spacing * (total_spots - 1))
            length = spot_length
            area = width * length
        else:
            charger_spacing = 1.15
            width = (spot_width * total_spots) + (charger_spacing * (total_spots - 1))
            length = spot_length
            area = width * length
        total_power = sum(config.power * config.quantity for config in charger_configs)
        transformer_area = 20 if total_power > 560 else 0
        total_area = (area + transformer_area) * 1.2
        auxiliary_area = 30
        return total_area + auxiliary_area

    def calculate_monthly_revenue(
        self,
        charger_configs: List[ChargerConfig],
        daily_vehicles_per_charger: int,
        avg_charge_time: float,
        peak_hour_ratio: float = 0.3,
        growth_rate: float = 0,
        location_factor: float = 1.0,
        additional_services: float = 0.0
    ) -> Dict:
        total_monthly_kwh = 0
        total_revenue = 0
        total_subsidy = 0
        for config in charger_configs:
            if config.type_name not in self.charger_configs:
                raise ValueError(f"Unknown charger type: {config.type_name}")
            power_per_charge = config.power * (avg_charge_time / 60)
            daily_kwh_per_charger = daily_vehicles_per_charger * power_per_charge
            monthly_kwh = daily_kwh_per_charger * config.quantity * 30
            peak_kwh = monthly_kwh * peak_hour_ratio
            normal_kwh = monthly_kwh * (1 - peak_hour_ratio)
            revenue = (peak_kwh * self.electricity_pricing.peak +
                      normal_kwh * self.electricity_pricing.normal)
            subsidy = monthly_kwh * self.electricity_pricing.vinfast_subsidy
            total_monthly_kwh += monthly_kwh
            total_revenue += revenue
            total_subsidy += subsidy
        base_total = total_revenue + total_subsidy
        base_total *= location_factor
        base_total += additional_services
        monthly_revenues = []
        months = 12 * 10
        for month in range(1, months + 1):
            year = (month - 1) // 12
            revenue_month = base_total * ((1 + growth_rate/100) ** year)
            monthly_revenues.append(revenue_month)
        return {
            'monthly_kwh': total_monthly_kwh,
            'base_revenue': base_total / 1_000_000,
            'subsidy': total_subsidy / 1_000_000,
            'total_revenue': (base_total) / 1_000_000,
            'monthly_revenues': monthly_revenues
        }

    def calculate_payback_period(
        self,
        investment: float,
        monthly_revenue: float,
        operating_costs: OperatingCosts,
        required_area: float,
        loan: Optional[LoanTerms] = None
    ) -> Dict:
        monthly_costs = (
            operating_costs.land_lease_per_m2 * required_area +
            operating_costs.staff +
            operating_costs.maintenance +
            operating_costs.other
        )
        if loan:
            loan_payment = self.calculate_loan_payments(loan)['monthly_payment']
            monthly_costs += loan_payment
        monthly_profit = monthly_revenue - monthly_costs
        if monthly_profit <= 0:
            return {
                'payback_months': float('inf'),
                'payback_years': float('inf'),
                'monthly_profit': 0,
                'is_profitable': False,
                'monthly_costs': monthly_costs / 1_000_000
            }
        payback_months = investment / monthly_profit
        return {
            'payback_months': payback_months,
            'payback_years': payback_months / 12,
            'monthly_profit': monthly_profit / 1_000_000,
            'monthly_costs': monthly_costs / 1_000_000,
            'is_profitable': True
        }

    def calculate_risk_metrics(
        self,
        monthly_revenue: float,
        operating_costs: OperatingCosts,
        scenarios: List[Dict]
    ) -> Dict:
        base_profit = monthly_revenue - sum([
            operating_costs.land_lease_per_m2,
            operating_costs.staff,
            operating_costs.maintenance,
            operating_costs.other
        ])
        scenario_results = []
        for scenario in scenarios:
            revenue_impact = monthly_revenue * (1 + scenario.get('revenue_change', 0))
            cost_impact = sum([
                operating_costs.land_lease_per_m2 * (1 + scenario.get('land_cost_change', 0)),
                operating_costs.staff * (1 + scenario.get('staff_cost_change', 0)),
                operating_costs.maintenance * (1 + scenario.get('maintenance_cost_change', 0)),
                operating_costs.other * (1 + scenario.get('other_cost_change', 0))
            ])
            profit = revenue_impact - cost_impact
            scenario_results.append({
                'scenario': scenario['name'],
                'profit': profit,
                'profit_change': (profit - base_profit) / base_profit if base_profit != 0 else 0
            })
        return {
            'base_profit': base_profit,
            'worst_case': min(s['profit'] for s in scenario_results),
            'best_case': max(s['profit'] for s in scenario_results),
            'scenarios': scenario_results
        }

    def calculate_sensitivity_analysis(
        self,
        charger_configs: List[ChargerConfig],
        daily_vehicles_per_charger: int,
        avg_charge_time: float,
        peak_hour_ratio: float,
        charging_price: float,
        electricity_cost: float,
        growth_rate: float = 0,
        location_factor: float = 1.0,
        additional_services: float = 0.0
    ) -> Dict:
        base = self.calculate_monthly_revenue(
            charger_configs,
            daily_vehicles_per_charger,
            avg_charge_time,
            peak_hour_ratio,
            growth_rate,
            location_factor,
            additional_services
        )
        base_revenue = base['total_revenue'] * 1_000_000
        scenarios_traffic = [0.7, 1.0, 1.3]
        traffic_results = []
        for factor in scenarios_traffic:
            rev = self.calculate_monthly_revenue(
                charger_configs,
                int(daily_vehicles_per_charger * factor),
                avg_charge_time,
                peak_hour_ratio,
                growth_rate,
                location_factor,
                additional_services
            )
            traffic_results.append({
                'scenario': f"Traffic {int(factor*100)}%",
                'total_revenue': rev['total_revenue']
            })
        scenarios_price = [0.8, 1.0, 1.2]
        price_results = []
        for factor in scenarios_price:
            original_peak = self.electricity_pricing.peak
            original_normal = self.electricity_pricing.normal
            self.electricity_pricing.peak = charging_price * factor
            self.electricity_pricing.normal = charging_price * factor * 0.8
            rev = self.calculate_monthly_revenue(
                charger_configs,
                daily_vehicles_per_charger,
                avg_charge_time,
                peak_hour_ratio,
                growth_rate,
                location_factor,
                additional_services
            )
            price_results.append({
                'scenario': f"Price {int(factor*100)}%",
                'total_revenue': rev['total_revenue']
            })
            self.electricity_pricing.peak = original_peak
            self.electricity_pricing.normal = original_normal
        scenarios_electricity = [0.85, 1.0, 1.15]
        elec_results = []
        for factor in scenarios_electricity:
            rev = self.calculate_monthly_revenue(
                charger_configs,
                daily_vehicles_per_charger,
                avg_charge_time,
                peak_hour_ratio,
                growth_rate,
                location_factor,
                additional_services
            )
            adjusted_revenue = rev['total_revenue'] * (1 - (factor - 1) * 0.15)
            elec_results.append({
                'scenario': f"Electricity Cost {int(factor*100)}%",
                'total_revenue': adjusted_revenue
            })
        return {
            'traffic_analysis': traffic_results,
            'price_analysis': price_results,
            'electricity_cost_analysis': elec_results
        }

    def calculate_roi(self, investment: float, monthly_revenue: float, operating_costs: OperatingCosts, required_area: float, analysis_years: int = 1) -> float:
        annual_profit = (monthly_revenue - (operating_costs.land_lease_per_m2 * required_area + operating_costs.staff + operating_costs.maintenance + operating_costs.other)) * 12
        return (annual_profit / investment) * 100

    def generate_annual_report(self, monthly_revenues: List[float]) -> List[Dict[str, Any]]:
        annual_report = []
        total_months = len(monthly_revenues)
        years = math.ceil(total_months / 12)
        for year in range(years):
            start = year * 12
            end = start + 12
            year_revenues = monthly_revenues[start:end]
            annual_report.append({
                'year': year + 1,
                'total_revenue': sum(year_revenues),
                'average_monthly_revenue': sum(year_revenues) / len(year_revenues)
            })
        return annual_report

    def suggest_optimal_pole_count(self, estimated_daily_vehicles: int, charger_configs: List[ChargerConfig]) -> int:
        total_poles = sum(config.quantity for config in charger_configs)
        optimal = total_poles
        if estimated_daily_vehicles > total_poles * 10:
            optimal = math.ceil(estimated_daily_vehicles / 10)
        return optimal
