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
    StationValidator
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

investment_period = st.sidebar.slider(
    "Thời gian đầu tư (năm)",
    min_value=1,
    max_value=10,
    value=5
)

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
        step=10.0
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
    
    loan_amount = st.number_input(
        "Số tiền vay (tỷ VND)",
        min_value=0.0,
        value=2.5,
        step=0.1
    )
    
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
    "Số xe mỗi trụ mỗi ngày",
    min_value=1,
    max_value=20,
    value=10
)

operation_cost = st.sidebar.number_input(
    "Chi phí vận hành (triệu VND/tháng)",
    min_value=0.0,
    value=20.0,
    step=5.0
)

if not charger_configs:
    st.error("Vui lòng chọn ít nhất một loại trụ sạc!")
    st.stop()

def calculate_required_area(charger_configs, mounting_type):
    if not charger_configs:
        return 0
        
    total_ports = sum(config.quantity * pole_types[config.type_name]["ports"] for config in charger_configs)
    mount_config = MOUNTING_TYPES[mounting_type]
    
    if mount_config["shared_width"]:
        rows = (total_ports + 1) // 2
        total_width = SPOT_WIDTH * rows
    else:
        total_width = SPOT_WIDTH * total_ports
    
    extra_space = 400  # Additional space for safety margins
    total_length = SPOT_LENGTH + extra_space
        
    return (total_length * total_width) / 1_000_000

required_area = calculate_required_area(charger_configs, mounting_type)
st.info(f"Diện tích đất cần thiết: {required_area:.1f}m²")

loan = LoanTerms(
    principal=loan_amount * 1_000_000_000,
    annual_rate=loan_rate / 100,
    term_months=loan_term * 12,
    start_date=datetime.now()
)

monthly_land_cost = land_cost_per_m2 * 1_000 * required_area

operating_costs = OperatingCosts(
    land_lease_per_m2=monthly_land_cost / required_area if required_area > 0 else 0,
    staff=10_000_000,
    maintenance=5_000_000,
    other=5_000_000
)

equipment_cost = sum(config.price * config.quantity for config in charger_configs)
total_power = sum(config.power * config.quantity for config in charger_configs)
transformer_cost = 800_000_000 if total_power > 560 else 0
total_equipment_cost = equipment_cost + transformer_cost

revenue = financials.calculate_monthly_revenue(
    charger_configs=charger_configs,
    daily_vehicles_per_charger=daily_vehicles_per_pole,
    avg_charge_time=20
)

loan_calc = financials.calculate_loan_payments(loan)
monthly_loan_payment = loan_calc['monthly_payment'] / 1_000_000

total_investment = total_equipment_cost + \
                   (monthly_land_cost * investment_period * 12)

payback = financials.calculate_payback_period(
    investment=total_investment,
    monthly_revenue=revenue['total_revenue'] * 1_000_000,
    operating_costs=operating_costs,
    required_area=required_area,
    loan=loan if loan_amount > 0 else None
)

monthly_costs = payback['monthly_costs']

st.header("Kết Quả Dự Đoán")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Tổng vốn đầu tư",
        f"{total_investment/1_000_000_000:.2f} tỷ VND",
        delta=f"Thiết bị: {total_equipment_cost/1_000_000_000:.2f} tỷ | Đất: {monthly_land_cost * investment_period * 12 / 1_000_000_000:.2f} tỷ/{investment_period} năm"
    )
    st.metric(
        "Doanh thu hàng tháng",
        f"{revenue['total_revenue']:.2f} triệu VND",
        delta=f"+{revenue['subsidy']:.1f}tr (trợ giá)"
    )

with col2:
    st.metric(
        "Chi phí hàng tháng",
        f"{monthly_costs:.2f} triệu VND",
        delta=f"Đất: {monthly_land_cost / 1_000_000:.1f}tr ({required_area:.1f}m²)"
    )
    st.metric(
        "Chi phí trả nợ hàng tháng",
        f"{monthly_loan_payment:.2f} triệu VND"
    )

with col3:
    st.metric(
        "Lợi nhuận hàng tháng",
        f"{payback['monthly_profit']:.2f} triệu VND"
    )
    payback_years = payback['payback_years']
    st.metric(
        "Thời gian hoàn vốn",
        f"{payback_years:.2f} năm" if payback['is_profitable'] else "Không hoàn vốn",
        delta=f"{'Khả thi' if payback_years <= investment_period else 'Vượt kỳ vọng'}" if payback['is_profitable'] else None
    )

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

st.header("Phân Tích Trực Quan")

months = list(range(1, investment_period * 12 + 1))
cumulative_profit = [payback['monthly_profit'] * i / 1_000_000 for i in months]
investment_line = [total_investment / 1_000_000] * len(months)

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
