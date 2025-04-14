import json
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

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
        peak_hour_ratio: float = 0.3
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
        return {
            'monthly_kwh': total_monthly_kwh,
            'base_revenue': total_revenue / 1_000_000,
            'subsidy': total_subsidy / 1_000_000,
            'total_revenue': (total_revenue + total_subsidy) / 1_000_000
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
                'profit_change': (profit - base_profit) / base_profit
            })
        return {
            'base_profit': base_profit,
            'worst_case': min(s['profit'] for s in scenario_results),
            'best_case': max(s['profit'] for s in scenario_results),
            'scenarios': scenario_results
        }
