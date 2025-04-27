import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from pathlib import Path

from financial import (
    ChargingStationFinancials,
    LoanTerms,
    ElectricityPricing,
    OperatingCosts,
    StationValidator,
    Investor,
    InvestorTerms
)

financials = ChargingStationFinancials("vinfast-charger.json")
validator = StationValidator("vinfast-charger.json")

st.title("Phân Tích Đầu Tư Trạm Sạc Xe Điện")
st.markdown("""
Ứng dụng này giúp bạn dự đoán chi phí, doanh thu, lợi nhuận và thời gian hoàn vốn khi đầu tư vào một trạm sạc xe điện.  
Điều chỉnh các tham số dưới đây để xem kết quả thay đổi.  
*Hướng dẫn*: Sử dụng các thanh trượt hoặc ô nhập liệu để thay đổi số liệu. Kết quả sẽ hiển thị ngay lập tức.
""")

st.sidebar.header("Tham Số Đầu Vào")

SPOT_LENGTH = 5400
SPOT_WIDTH = 2500

MOUNTING_TYPES = {
    "wall": {"spots_per_charger": 1, "shared_width": False},
    "side": {"spots_per_charger": 2, "shared_width": True},
    "rear": {"spots_per_charger": 1, "shared_width": False}
}

pole_types = {
    "Trụ sạc ô tô - Sạc nhanh DC 20kW Link": {"cost": 100_000_000, "power": 20, "ports": 1},
    "Trụ sạc ô tô - Sạc nhanh DC 30kW": {"cost": 143_000_000, "power": 30, "ports": 1},
    "Trụ sạc ô tô - Sạc nhanh DC 60kW": {"cost": 278_000_000, "power": 60, "ports": 2},
    "Trụ sạc ô tô - Sạc siêu nhanh DC 120kW": {"cost": 416_000_000, "power": 120, "ports": 2},
    "Trụ sạc ô tô - Sạc siêu nhanh DC 150kW": {"cost": 526_000_000, "power": 150, "ports": 2}
}

class ChargerConfig:
    def __init__(self, type_name, quantity, power, price):
        self.type_name = type_name
        self.quantity = quantity
        self.power = power
        self.price = price

st.sidebar.subheader("Cấu hình trụ sạc")
charger_configs = []

# Investor configuration
st.sidebar.subheader("Cấu hình nhà đầu tư")
total_investment = st.sidebar.number_input(
    "Tổng vốn đầu tư (triệu VND)",
    min_value=0.0,
    value=0.0,
    step=10.0,
    key="total_investment"
) * 1_000_000  # Convert to VND

# total_investment = investment_details['total'] * 1_000_000

num_investors = st.sidebar.number_input(
    "Số lượng nhà đầu tư",
    min_value=1,
    max_value=10,
    value=1,
    key="num_investors"
)

investors = []
for i in range(num_investors):
    with st.sidebar.expander(f"Nhà đầu tư {i+1}"):
        name = st.text_input(
            f"Tên nhà đầu tư {i+1}",
            value=f"Nhà đầu tư {i+1}",
            key=f"investor_name_{i}"
        )
        default_contrib = round(100 / num_investors)
        contribution = st.slider(
            f"Tỷ lệ đóng góp (%)",
            min_value=0,
            max_value=100,
            value=default_contrib,
            key=f"investor_contribution_{i}"
        )
        own_capital = st.slider(
            f"Tỷ lệ vốn tự có (%)",
            min_value=0,
            max_value=100,
            value=100,
            key=f"investor_own_capital_{i}"
        )
        commitment_years = st.slider(
            f"Thời gian cam kết đầu tư (năm)",
            min_value=1,
            max_value=10,
            value=5,
            key=f"investor_commitment_{i}"
        )
        
        # Calculate monetary values
        total_contribution = total_investment * (contribution / 100)
        own_amount = total_contribution * (own_capital / 100)
        borrowed_amount = total_contribution - own_amount
        
        st.write(f"Tổng đóng góp: {total_contribution/1_000_000:.2f} triệu VND")
        st.write(f"Vốn tự có: {own_amount/1_000_000:.2f} triệu VND")
        st.write(f"Vốn vay: {borrowed_amount/1_000_000:.2f} triệu VND")
        
        # Create loan terms if borrowed
        loan_terms = None
        if borrowed_amount > 0:
            loan_rate = st.slider(
                f"Lãi suất vay (%)",
                min_value=5.0,
                max_value=15.0,
                value=12.0,
                key=f"investor_loan_rate_{i}"
            )
            loan_term = st.slider(
                f"Thời hạn vay (năm)",
                min_value=1,
                max_value=10,
                value=5,
                key=f"investor_loan_term_{i}"
            )
            loan_terms = LoanTerms(
                principal=borrowed_amount,
                annual_rate=loan_rate/100,
                term_months=loan_term*12,
                start_date=datetime.now()
            )
        
        investors.append(Investor(
            name=name,
            contribution_percent=contribution,
            own_capital_percent=own_capital,
            loan_terms=loan_terms,
            withdrawal_risk=0.0,
            commitment_years=commitment_years
        ))

        # After collecting all investors, normalize the percentages
        total_percent = sum(inv.contribution_percent for inv in investors)
        if total_percent > 0:
            for inv in investors:
                inv.contribution_percent = (inv.contribution_percent / total_percent) * 100

def get_display_name(full_name):
    if "Link" in full_name:
        return "Sạc nhanh DC 20kW"
    return full_name.replace("Trụ sạc ô tô - ", "")

for pole_type, info in pole_types.items():
    col1, col2 = st.sidebar.columns(2)
    display_name = get_display_name(pole_type)
    quantity = col1.number_input(
        f"Số lượng {display_name}",
        min_value=0,
        max_value=10,
        value=0,
        key=f"quantity_{display_name}"
    )
    if quantity > 0:
        charger_configs.append(
            ChargerConfig(
                type_name=pole_type,
                quantity=quantity,
                power=info["power"],
                price=info["cost"]
            )
        )

with st.sidebar.expander("Tham số nâng cao"):
    land_cost_per_m2 = st.number_input(
        "Chi phí thuê đất (nghìn VND/m²/tháng)",
        min_value=0.0,
        value=100.0,
        step=10.0,
        key="land_cost_per_m2"
    )
    
    total_station_power_kw = sum(config.power * config.quantity for config in charger_configs)
    st.metric("Tổng công suất trạm", f"{total_station_power_kw:.0f} kW")

    transformer_cost_per_kw = st.number_input(
        "Chi phí biến áp (VND/kW)",
        min_value=1_000_000,
        max_value=5_000_000,
        value=2_315_000,
        step=50_000,
        key="transformer_cost_per_kw",
        help="Chi phí ước tính cho mỗi kW công suất lắp đặt trạm biến áp."
    )
    
    mounting_type = st.selectbox(
        "Kiểu lắp đặt trụ sạc",
        ["wall", "side", "rear"],
        format_func=lambda x: {
            "wall": "Gắn tường (1 trụ/1 vị trí)",
            "side": "Bên hông (1 trụ/2 vị trí)",
            "rear": "Phía sau (1 trụ/1 vị trí)"
        }[x]
    )
    
    driving_lane_width = st.number_input(
        "Độ rộng làn xe (m)",
        min_value=3.0,
        max_value=10.0,
        value=6.0,
        step=0.5
    )
    
    loan_amount = 0
    loan_rate = st.slider(
        "Lãi suất vay (%/năm)",
        min_value=5.0,
        max_value=15.0,
        value=12.0,
        step=0.1
    )
    
    loan_term = st.slider(
        "Thời hạn vay (năm)",
        min_value=1,
        max_value=10,
        value=5
    )

daily_vehicles_per_pole = st.sidebar.slider(
    "Số xe trung bình mỗi trụ mỗi ngày",
    min_value=1,
    max_value=30,
    value=10
)

avg_charge_time_input = st.sidebar.slider(
    "Thời gian sạc trung bình (phút)",
    min_value=10,
    max_value=120,
    value=30,
    step=5
)

additional_monthly_income_input = st.sidebar.number_input(
    "Thu nhập phụ hàng tháng (triệu VND)",
    min_value=0.0,
    value=0.0,
    step=1.0,
    key="additional_income",
    help="Thu nhập thêm từ các dịch vụ khác như cafe, đồ ăn..."
)

if not charger_configs:
    st.error("Vui lòng chọn ít nhất một loại trụ sạc!")
    st.stop()

required_area = financials.calculate_required_area(
    charger_configs=charger_configs,
    mounting_type=mounting_type,
    driving_lane_width=driving_lane_width
)
st.info(f"Diện tích đất cần thiết: {required_area:.1f}m²")

loan = None
monthly_land_cost = land_cost_per_m2 * 1_000 * required_area

operating_costs = OperatingCosts(
    land_lease_per_m2=land_cost_per_m2 * 1000,
    staff=10_000_000,
    maintenance=5_000_000,
    other=5_000_000
)
monthly_land_cost = (land_cost_per_m2 * 1000) * required_area

revenue = financials.calculate_monthly_revenue(
    charger_configs=charger_configs,
    daily_vehicles_per_charger=daily_vehicles_per_pole,
    avg_charge_time=avg_charge_time_input
)
total_monthly_kwh = revenue['monthly_kwh']

investment_details = financials.calculate_total_investment(
    charger_configs=charger_configs,
    required_area=required_area,
    operating_costs=operating_costs,
    total_power_kw=total_station_power_kw,
    transformer_cost_per_kw=transformer_cost_per_kw
)
total_investment_vnd = investment_details['total'] * 1_000_000

loan = LoanTerms(
    principal=total_investment_vnd,
    annual_rate=loan_rate / 100,
    term_months=loan_term * 12,
    start_date=datetime.now()
)

loan_calc = financials.calculate_loan_payments(loan)
monthly_loan_payment = loan_calc['monthly_payment'] / 1_000_000

payback = financials.calculate_payback_period(
    total_investment=total_investment_vnd,
    monthly_revenue=revenue['total_revenue'] * 1_000_000,
    operating_costs=operating_costs,
    required_area=required_area,
    total_monthly_kwh=total_monthly_kwh,
    electricity_pricing=financials.electricity_pricing,
    additional_monthly_income=additional_monthly_income_input * 1_000_000,
    loan=loan
)

st.header("Kết Quả Dự Đoán")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Tổng vốn đầu tư",
        f"{investment_details['total']:.2f} triệu VND"
    )
    st.write(f"Chi tiết đầu tư:")
    st.write(f"- Trụ sạc: {investment_details['charger_costs']:.1f} triệu VND")
    st.write(f"- Biến áp: {investment_details['transformer_cost']:.1f} triệu VND")
    st.write(f"- NLMT: {investment_details['solar_panel_cost']:.1f} triệu VND")
    st.write(f"- Cọc đất: {investment_details['land_deposit']:.1f} triệu VND")
    st.write(f"- Sai số: {investment_details['error_margin']:.1f} triệu VND")
    
    st.metric(
        "Doanh thu hàng tháng (sau chia sẻ)",
        f"{revenue['total_revenue']:.2f} triệu VND"
    )
    st.write(f"Chi tiết doanh thu:")
    st.write(f"- Tiền sạc: {revenue['base_revenue']:.2f} triệu VND")
    st.write(f"- Phí quá giờ: {revenue['overage_fees']:.2f} triệu VND")

with col2:
    monthly_op_cost = payback['monthly_operating_costs']
    monthly_elec_cost = payback['monthly_electricity_cost']
    total_monthly_cost = payback['monthly_costs']

    loan_display = f"{monthly_loan_payment:.2f}tr" if loan_calc['monthly_payment'] > 0 else "0tr"

    st.metric(
        "Tổng chi phí hàng tháng",
        f"{total_monthly_cost:.2f} triệu VND"
    )
    st.write(f"Chi tiết chi phí:")
    st.write(f"- Vận hành: {monthly_op_cost:.1f} triệu VND")
    st.write(f"- Điện: {monthly_elec_cost:.1f} triệu VND")
    st.write(f"- Trả nợ: {loan_display}")
    
    st.metric(
        "Chi phí thuê đất hàng tháng",
        f"{monthly_land_cost / 1_000_000:.1f} triệu VND"
    )
    st.write(f"Diện tích: {required_area:.1f}m²")

with col3:
    st.metric(
        "Lợi nhuận hàng tháng",
        f"{payback['monthly_profit']:.2f} triệu VND"
    )
    st.write("Chi tiết lợi nhuận:")
    st.write(f"- Thu nhập phụ: {additional_monthly_income_input:.1f} triệu VND")
    st.write(f"- Biên lợi nhuận: {payback['profit_margin']:.1f}%")
    
    payback_years = payback['payback_years']
    st.metric(
        "Thời gian hoàn vốn",
        f"{payback_years:.2f} năm" if payback['is_profitable'] else "Không hoàn vốn"
    )
    if payback['is_profitable']:
        investment_period = max(inv.commitment_years for inv in investors)
        st.write("Đánh giá:")
        st.write(f"- {'Khả thi' if payback_years <= investment_period else 'Vượt kỳ vọng'}")

# Investor results
if num_investors > 1:
    st.subheader("Phân bổ lợi nhuận cho nhà đầu tư")
    
    # Create investor terms with updated investor objects 
    investor_terms = InvestorTerms(
        investors=investors,
        total_investment=total_investment
    )
    
    # Calculate profit sharing with updated investor terms
    profit_shares = financials.calculate_monthly_profit_sharing(
        monthly_profit=payback['monthly_profit'] * 1_000_000,
        investor_terms=investor_terms
    )
    
    # Create DataFrame with updated profit sharing data
    investor_data = []
    for inv in investors:
        share = profit_shares['profit_shares'][inv.name]
        monthly_loan_payment = 0
        if inv.loan_terms:
            loan_payment = financials.calculate_loan_payments(inv.loan_terms)
            monthly_loan_payment = loan_payment['monthly_payment'] / 1_000_000
        investor_data.append({
            'Nhà đầu tư': inv.name,
            'Tỷ lệ đóng góp': f"{share['contribution_percent']:.1f}%",
            'Lợi nhuận hàng tháng': f"{share['gross_share']/1_000_000:.2f} triệu VND",
            'Trả nợ hàng tháng': f"{monthly_loan_payment:.2f} triệu VND", 
            'Thu nhập ròng': f"{share['gross_share']/1_000_000 - monthly_loan_payment:.2f} triệu VND",
            'Rủi ro rút vốn': f"{share['withdrawal_risk']*100:.0f}%"
        })
    
    # Update table with new data
    df_investors = pd.DataFrame(investor_data)
    st.table(df_investors)
    
    # Rest of the withdrawal simulation code remains unchanged
    selected_investor = st.selectbox(
        "Mô phỏng rút vốn",
        options=[inv.name for inv in investors],
        index=0,
        key="withdrawal_sim"
    )
    
    if st.button("Mô phỏng rút vốn"):
        withdrawal_result = financials.simulate_capital_withdrawal(
            investor_name=selected_investor,
            investor_terms=investor_terms,
            years=next(inv.commitment_years for inv in investors if inv.name == selected_investor),
            withdraw_percent=100,
            monthly_profit=payback['monthly_profit'] * 1_000_000
        )
        
        st.warning(f"Kết quả mô phỏng rút vốn của {selected_investor}:")
        st.write(f"- Vốn rút: {withdrawal_result['withdrawn_capital']/1_000_000:.2f} triệu VND")
        st.write(f"- Phạt rút vốn: {withdrawal_result['penalty']/1_000_000:.2f} triệu VND")
        st.write(f"- Nhà đầu tư còn lại: {', '.join(withdrawal_result['remaining_investors'])}")
        
        new_shares = []
        for name, share in withdrawal_result['new_profit_shares']['profit_shares'].items():
            new_shares.append({
                'Nhà đầu tư': name,
                'Tỷ lệ sở hữu mới': f"{share['percentage']*100:.1f}%",
                'Lợi nhuận mới': f"{share['share']/1_000_000:.2f} triệu VND"
            })
        
        st.table(pd.DataFrame(new_shares))

risk_scenarios = [
    {
        'name': 'Lạc quan',
        'revenue_change': 0.2,
        'land_cost_change': 0,
        'staff_cost_change': 0,
        'maintenance_cost_change': 0,
        'other_cost_change': 0
    },
    {
        'name': 'Thận trọng',
        'revenue_change': -0.1,
        'land_cost_change': 0.1,
        'staff_cost_change': 0.1,
        'maintenance_cost_change': 0.1,
        'other_cost_change': 0.1
    },
    {
        'name': 'Rủi ro cao',
        'revenue_change': -0.3,
        'land_cost_change': 0.2,
        'staff_cost_change': 0.2,
        'maintenance_cost_change': 0.3,
        'other_cost_change': 0.2
    }
]

risk_metrics = financials.calculate_risk_metrics(
    monthly_revenue=revenue['total_revenue'] * 1_000_000,
    operating_costs=operating_costs,
    scenarios=risk_scenarios
)

investment_period = max(inv.commitment_years for inv in investors)
st.header("Phân Tích Trực Quan")
months = list(range(1, investment_period * 12 + 1))

cumulative_profit = [payback['monthly_profit'] * i for i in months]
investment_line = [investment_details['total']] * len(months)

MOUNTING_NAMES = {
    "wall": "Gắn tường",
    "side": "Bên hông",
    "rear": "Phía sau"
}

if required_area > 0:
    st.markdown(f"""
    ### Chi tiết diện tích
    - Kích thước mỗi vị trí đỗ xe: {SPOT_LENGTH/1000:.1f}m x {SPOT_WIDTH/1000:.1f}m
    - Kiểu lắp đặt trụ sạc: {MOUNTING_NAMES[mounting_type]}
    - Tổng diện tích mặt bằng: {required_area:.1f}m²
    - Chi phí thuê đất hàng tháng: {monthly_land_cost/1_000_000:.1f} triệu đồng
    """)

df = pd.DataFrame({
    'Tháng': months,
    'Lợi nhuận tích lũy (triệu VND)': cumulative_profit,
    'Vốn đầu tư (triệu VND)': investment_line
})

fig = px.line(
    df,
    x='Tháng',
    y=['Lợi nhuận tích lũy (triệu VND)', 'Vốn đầu tư (triệu VND)'],
    title='Lợi nhuận tích lũy qua thời gian'
)
if payback['is_profitable']:
    fig.add_vline(
        x=payback['payback_months'],
        line_dash="dash",
        line_color="green",
        annotation_text="Điểm hoàn vốn"
    )
st.plotly_chart(fig)

risk_data = pd.DataFrame([
    {
        'Kịch bản': s['name'],
        'Lợi nhuận (triệu VND/tháng)': m['profit'] / 1_000_000
    }
    for s, m in zip(risk_scenarios, risk_metrics['scenarios'])
])

fig_risk = px.bar(
    risk_data,
    x='Kịch bản',
    y='Lợi nhuận (triệu VND/tháng)',
    title='Phân tích rủi ro theo kịch bản',
    color='Kịch bản'
)
st.plotly_chart(fig_risk)

st.markdown("---")
st.write("Ứng dụng này được thiết kế để hỗ trợ quyết định đầu tư. Hãy liên hệ để biết thêm chi tiết!")