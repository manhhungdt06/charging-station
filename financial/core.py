from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, time

@dataclass
class Investor:
    name: str
    contribution_percent: float  # Percentage of total investment (0-100)
    own_capital_percent: float  # Percentage of contribution that is own capital (0-100)
    loan_terms: Optional[LoanTerms] = None  # Loan details for borrowed portion
    withdrawal_risk: float = 0.0  # 0-1 probability
    active: bool = True
    commitment_years: int = 5  # Years of commitment

    @property
    def borrowed_percent(self) -> float:
        return 100 - self.own_capital_percent

@dataclass
class InvestorTerms:
    investors: List[Investor] = field(default_factory=list)
    total_investment: float = 0.0  # Total investment amount in VND
    profit_sharing_model: str = "capital"  # Options: "capital", "equal", "custom"
    withdrawal_penalty: float = 0.1  # 10% penalty on withdrawn capital

    def validate_investors(self):
        """Validate that investor percentages sum to 100%"""
        total_percent = sum(inv.contribution_percent for inv in self.investors)
        if not (99 <= total_percent <= 101):  # Allow a 1% deviation
            raise ValueError(f"Investor contributions must sum to 100%, got {total_percent}%")

@dataclass 
class LoanTerms:
    principal: float
    annual_rate: float
    term_months: int
    start_date: datetime

@dataclass
class TimeRange:
    start: time
    end: time

@dataclass
class DaySchedule:
    normal: List[TimeRange]
    peak: List[TimeRange]
    off_peak: List[TimeRange]

@dataclass
class ElectricityPricing:
    normal: float = 1728
    peak: float = 3116
    off_peak: float = 1094
    vinfast_rate: float = 3858 # Keep for potential future use, but revenue calc uses owner_share
    owner_share_per_kwh: float = 750 # Owner's revenue share from VinFast
    vinfast_subsidy: float = 0
    weekday_schedule: DaySchedule = None
    weekend_schedule: DaySchedule = None

    def __post_init__(self):
        if not self.weekday_schedule:
            self.weekday_schedule = DaySchedule(
                normal=[
                    TimeRange(time(4, 0), time(9, 30)),
                    TimeRange(time(11, 30), time(17, 0)),
                    TimeRange(time(20, 0), time(22, 0))
                ],
                peak=[
                    TimeRange(time(9, 30), time(11, 30)),
                    TimeRange(time(17, 0), time(20, 0))
                ],
                off_peak=[TimeRange(time(22, 0), time(4, 0))]
            )
        if not self.weekend_schedule:
            self.weekend_schedule = DaySchedule(
                normal=[TimeRange(time(4, 0), time(22, 0))],
                peak=[],
                off_peak=[TimeRange(time(22, 0), time(4, 0))]
            )

# TransformerStation dataclass removed as cost is now calculated based on kW

@dataclass
class SolarPanelConfig:
    installed: bool = False
    capacity_kw: float = 0
    price_per_kw: float = 15_000_000

@dataclass
class OperatingCosts:
    land_lease_per_m2: float
    staff: float = 10_000_000
    maintenance: float = 5_000_000
    other: float = 5_000_000
    land_lease_deposit_months: int = 6
    additional_monthly_income: float = 0
    capacity_fee_per_kw: float = 0
    insurance_cost: float = 3_000_000
    marketing_cost: float = 2_000_000
    working_capital_months: int = 2  # Months of electricity to prepay

@dataclass
class ChargingTimeConfig:
    time_limit_minutes: int = 30
    overage_fee_per_minute: float = 1000

@dataclass
class ChargerConfig:
    type_name: str
    quantity: int
    power: float
    price: float

@dataclass
class VehicleModel:
    name: str
    battery_capacity: float
    consumption_per_100km: float

class ChargingStationFinancials:
    def __init__(
        self,
        config_path: str = "vinfast-charger.json",
        # transformer parameter removed
        solar_config: Optional[SolarPanelConfig] = None,
        charging_config: Optional[ChargingTimeConfig] = None
    ):
        self.charger_configs = self._load_charger_configs(config_path)
        self.electricity_pricing = ElectricityPricing()
        # self.transformer removed
        self.solar_config = solar_config or SolarPanelConfig()
        self.charging_config = charging_config or ChargingTimeConfig()
        self.vehicle_models = self._load_vehicle_models()
    
    def _load_vehicle_models(self) -> List[VehicleModel]:
        return [
            VehicleModel("VinFast VF3", 42, 13.57),
            VehicleModel("VinFast VF5", 37, 16.0),
            VehicleModel("VinFast VF6", 60, 15.0),
            VehicleModel("VinFast VF7", 75, 17.0),
            VehicleModel("VinFast VF8", 82, 18.5),
            VehicleModel("VinFast VF9", 95, 20.0)
        ]
    
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

    def calculate_required_area(
        self,
        charger_configs: List[ChargerConfig],
        mounting_type: str,
        driving_lane_width: float = 6.0
    ) -> float:
        spot_length = 5.4
        spot_width = 2.5
        total_chargers = sum(config.quantity for config in charger_configs)
        
        # Simplified layout assumption: single row of spots with one driving lane
        # More complex layouts would require more detailed parameters
        
        if mounting_type == "wall":
            # Spots side-by-side
            total_width = spot_width * total_chargers
            total_length = spot_length + driving_lane_width # Lane runs parallel to spots
            parking_area = total_width * spot_length
            lane_area = total_width * driving_lane_width
        elif mounting_type == "side":
            # Assuming chargers placed between pairs of spots
            charger_spacing = 0.9
            num_pairs = (total_chargers + 1) // 2 # Number of charger units
            total_width = (spot_width * total_chargers) + (charger_spacing * max(0, num_pairs - 1))
            total_length = spot_length + driving_lane_width
            parking_area = total_width * spot_length
            lane_area = total_width * driving_lane_width
        else: # rear mounting
            charger_spacing = 1.15
            total_width = (spot_width * total_chargers) + (charger_spacing * max(0, total_chargers - 1))
            total_length = spot_length + driving_lane_width
            parking_area = total_width * spot_length
            lane_area = total_width * driving_lane_width

        base_area = parking_area + lane_area

        total_power = sum(config.power * config.quantity for config in charger_configs)
        transformer_area = 20 if total_power > 560 else 0
        
        # Apply overhead and auxiliary area to the calculated base area
        total_area = (base_area + transformer_area) * 1.2
        auxiliary_area = 30
        
        return total_area + auxiliary_area

    def calculate_monthly_revenue(
        self,
        charger_configs: List[ChargerConfig],
        daily_vehicles_per_charger: int,
        avg_charge_time: float
    ) -> Dict:
        total_monthly_kwh = 0
        total_overage_fees = 0
        
        for config in charger_configs:
            if config.type_name not in self.charger_configs:
                raise ValueError(f"Unknown charger type: {config.type_name}")
            
            power_per_charge = config.power * (avg_charge_time / 60)
            daily_kwh_per_charger = daily_vehicles_per_charger * power_per_charge
            monthly_kwh = daily_kwh_per_charger * config.quantity * 30
            
            # Calculate overage fees
            if avg_charge_time > self.charging_config.time_limit_minutes:
                overage_minutes = avg_charge_time - self.charging_config.time_limit_minutes
                daily_overage = (overage_minutes * self.charging_config.overage_fee_per_minute *
                               daily_vehicles_per_charger * config.quantity)
                total_overage_fees += daily_overage * 30
            
            total_monthly_kwh += monthly_kwh

        # VinFast pays owner 750 VND/kWh regardless of time of use
        owner_revenue = total_monthly_kwh * self.electricity_pricing.owner_share_per_kwh
        
        return {
            'monthly_kwh': total_monthly_kwh,
            'base_revenue': owner_revenue / 1_000_000,
            'overage_fees': total_overage_fees / 1_000_000,
            'total_revenue': (owner_revenue + total_overage_fees) / 1_000_000
        }
    
    def calculate_total_investment(
        self,
        charger_configs: List[ChargerConfig],
        required_area: float,
        operating_costs: OperatingCosts,
        total_power_kw: float, # Added total power
        transformer_cost_per_kw: float, # Added cost per kW
        error_margin: float = 0.1
    ) -> Dict:
        charger_costs = sum(config.price * config.quantity for config in charger_configs)
        # Calculate transformer price based on total power and cost per kW
        transformer_price = total_power_kw * transformer_cost_per_kw
        solar_costs = (self.solar_config.capacity_kw * self.solar_config.price_per_kw
                      if self.solar_config.installed else 0)
        land_deposit = (operating_costs.land_lease_per_m2 * required_area *
                       operating_costs.land_lease_deposit_months)
        
        base_investment = charger_costs + transformer_price + solar_costs + land_deposit
        error_amount = base_investment * error_margin
        
        return {
            'charger_costs': charger_costs / 1_000_000,
            'transformer_cost': transformer_price / 1_000_000,
            'solar_panel_cost': solar_costs / 1_000_000,
            'land_deposit': land_deposit / 1_000_000,
            'error_margin': error_amount / 1_000_000,
            'total': (base_investment + error_amount) / 1_000_000
        }

    def calculate_payback_period(
        self,
        monthly_revenue: float,
        required_area: float,
        total_investment: float,
        total_monthly_kwh: float,
        electricity_pricing: ElectricityPricing,
        operating_costs: OperatingCosts,
        additional_monthly_income: float = 0,
        loan: Optional[LoanTerms] = None,
        electricity_cost_per_kwh: float = 4500,  # Actual EVN rate
        total_power_kw: float = 0  # Total station power in kW
    ) -> Dict:
        # Calculate full monthly operating costs including capacity fees and insurance
        monthly_operating_costs = (
            operating_costs.land_lease_per_m2 * required_area +
            operating_costs.staff +
            operating_costs.maintenance +
            operating_costs.other +
            operating_costs.capacity_fee_per_kw * total_power_kw +
            operating_costs.insurance_cost +
            operating_costs.marketing_cost
        )

        # Calculate working capital cost for electricity prepayment
        monthly_electricity_cost = total_monthly_kwh * electricity_cost_per_kwh
        working_capital_cost = (
            monthly_electricity_cost * operating_costs.working_capital_months * 
            (loan.annual_rate/12 if loan else 0.01)  # 1% opportunity cost if no loan
        )
        
        # Monthly costs are just operating costs since VinFast pays for electricity
        monthly_costs = monthly_operating_costs
        
        if loan:
            loan_payment = self.calculate_loan_payments(loan)['monthly_payment']
            monthly_costs += loan_payment

        # Calculate total monthly income (owner's share from VinFast + additional income)
        owner_revenue = total_monthly_kwh * electricity_pricing.owner_share_per_kwh
        total_monthly_income = owner_revenue + additional_monthly_income
        
        # Calculate monthly profit
        monthly_profit = total_monthly_income - monthly_costs
        
        # Calculate payback period only if profit is positive
        if monthly_profit > 0:
            payback_months = total_investment / monthly_profit
            is_profitable = True
        else:
            payback_months = float('inf')
            is_profitable = False

        profit_margin = (monthly_profit / total_monthly_income * 100) if total_monthly_income > 0 else 0
        return {
            'payback_months': payback_months,
            'payback_years': payback_months / 12,
            'monthly_profit': monthly_profit / 1_000_000,
            'monthly_costs': monthly_costs / 1_000_000,
            'monthly_operating_costs': monthly_operating_costs / 1_000_000,
            'monthly_electricity_cost': 0,  # VinFast pays for electricity
            'is_profitable': is_profitable,
            'profit_margin': profit_margin
        }
    
    def calculate_investor_shares(
        self,
        investor_terms: InvestorTerms
    ) -> Dict[str, Any]:
        """Calculate each investor's share of costs and profits based on percentage contributions."""
        investor_terms.validate_investors()
        
        investment_shares = {}
        for investor in investor_terms.investors:
            # Calculate monetary amounts
            total_contribution = investor_terms.total_investment * (investor.contribution_percent / 100)
            own_capital = total_contribution * (investor.own_capital_percent / 100)
            borrowed_capital = total_contribution - own_capital
            
            # Calculate loan payments if applicable
            loan_payment = 0
            if investor.loan_terms and borrowed_capital > 0:
                loan_payment = self.calculate_loan_payments(investor.loan_terms)['monthly_payment']
            
            investment_shares[investor.name] = {
                'contribution_percent': investor.contribution_percent,
                'total_contribution': total_contribution,
                'own_capital': own_capital,
                'borrowed_capital': borrowed_capital,
                'loan_payment': loan_payment,
                'withdrawal_risk': investor.withdrawal_risk,
                'active': investor.active
            }
        
        return {
            'total_investment': investor_terms.total_investment,
            'investment_shares': investment_shares,
            'profit_sharing_model': investor_terms.profit_sharing_model
        }

    def calculate_monthly_profit_sharing(
        self,
        monthly_profit: float,
        investor_terms: InvestorTerms
    ) -> Dict[str, Any]:
        """Calculate profit distribution among investors based on percentage contributions."""
        shares = self.calculate_investor_shares(investor_terms)
        
        profit_shares = {}
        for name, data in shares['investment_shares'].items():
            if not data['active']:
                continue
                
            if investor_terms.profit_sharing_model == "equal":
                share = monthly_profit / len([inv for inv in investor_terms.investors if inv.active])
            else:  # capital-based sharing
                share = monthly_profit * (data['contribution_percent'] / 100)
            
            # Calculate net profit after loan payments
            net_share = share - data.get('loan_payment', 0)
            
            profit_shares[name] = {
                'gross_share': share,
                'net_share': net_share,
                'loan_payment': data.get('loan_payment', 0),
                'contribution_percent': data['contribution_percent'],
                'withdrawal_risk': data['withdrawal_risk']
            }
        
        return {
            'total_profit': monthly_profit,
            'profit_shares': profit_shares,
            'sharing_model': investor_terms.profit_sharing_model
        }

    def simulate_capital_withdrawal(
        self,
        investor_name: str,
        investor_terms: InvestorTerms,
        monthly_profit: float
    ) -> Dict[str, Any]:
        """Simulate the impact of an investor withdrawing their capital."""
        # Find the investor
        investor = next((inv for inv in investor_terms.investors if inv.name == investor_name), None)
        if not investor:
            raise ValueError(f"Investor {investor_name} not found")
        
        # Calculate total contribution and penalty
        total_contribution = investor_terms.total_investment * (investor.contribution_percent / 100)
        penalty = total_contribution * investor_terms.withdrawal_penalty
        
        # Update investor status
        investor.active = False
        
        # Recalculate shares without this investor
        remaining_investors = [inv for inv in investor_terms.investors if inv.active]
        
        # Adjust percentages for remaining investors
        remaining_percent = sum(inv.contribution_percent for inv in remaining_investors)
        for inv in remaining_investors:
            inv.contribution_percent = (inv.contribution_percent / remaining_percent) * 100
        
        # Calculate new profit distribution
        profit_shares = self.calculate_monthly_profit_sharing(monthly_profit, investor_terms)
        
        return {
            'withdrawn_capital': total_contribution,
            'penalty': penalty,
            'remaining_investors': [inv.name for inv in remaining_investors],
            'new_profit_shares': profit_shares,
            'new_total_investment': investor_terms.total_investment - total_contribution
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
