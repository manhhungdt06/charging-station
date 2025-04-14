import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from financial import (
    ChargingStationFinancials,
    LoanTerms,
    OperatingCosts,
    StationValidator,
)
from financial.core import ChargerConfig

st.title("Phân Tích Đầu Tư Trạm Sạc Xe Điện")

st.markdown("""
Điều chỉnh các tham số dưới đây để xem kết quả thay đổi.
""")

st.sidebar.header("Cấu hình trụ sạc")
charger_configs = []
pole_types = {
    "Trụ sạc ô tô - Sạc nhanh DC 20kW Link": {"cost": 100_000_000, "power": 20},
    "Trụ sạc ô tô - Sạc nhanh DC 30kW": {"cost": 143_000_000, "power": 30},
    "Trụ sạc ô tô - Sạc nhanh DC 60kW": {"cost": 278_000_000, "power": 60},
    "Trụ sạc ô tô - Sạc siêu nhanh DC 120kW": {"cost": 416_000_000, "power": 120},
    "Trụ sạc ô tô - Sạc siêu nhanh DC 150kW": {"cost": 526_000_000, "power": 150}
}
for pole_type, info in pole_types.items():
    quantity = st.sidebar.number_input(f"Số lượng {pole_type}", min_value=0, max_value=10, value=0, key=pole_type)
    if quantity > 0:
        charger_configs.append(ChargerConfig(type_name=pole_type, quantity=quantity, power=info["power"], price=info["cost"]))

if not charger_configs:
    st.error("Vui lòng chọn ít nhất một loại trụ sạc!")
    st.stop()

st.sidebar.header("Tham số kinh doanh")
daily_vehicles = st.sidebar.slider("Số xe mỗi trụ mỗi ngày", min_value=1, max_value=30, value=10)
avg_charge_time = st.sidebar.number_input("Thời gian sạc trung bình (phút)", min_value=5.0, max_value=60.0, value=20.0)
growth_rate = st.sidebar.slider("Tốc độ tăng trưởng hàng năm (%)", min_value=0, max_value=50, value=10)
location_factor = st.sidebar.slider("Hệ số vị trí địa lý", min_value=0.5, max_value=2.0, value=1.0)
additional_services = st.sidebar.number_input("Doanh thu từ dịch vụ phụ trợ (VND/tháng)", min_value=0.0, value=15_000_000.0, step=1_000_000.0)

st.sidebar.header("Chi phí đầu tư và vận hành")
equipment_cost = sum(config.price * config.quantity for config in charger_configs)
transformer_cost = st.sidebar.number_input("Chi phí trạm biến áp (VND)", min_value=0.0, value=800_000_000.0, step=10_000_000.0)
land_cost = st.sidebar.number_input("Chi phí thuê mặt bằng (VND/tháng)", min_value=0.0, value=10_000_000.0, step=1_000_000.0)
staff_cost = st.sidebar.number_input("Chi phí nhân viên (VND/tháng)", min_value=0.0, value=16_000_000.0, step=1_000_000.0)
other_expenses = st.sidebar.number_input("Chi phí khác (VND/tháng)", min_value=0.0, value=5_000_000.0, step=1_000_000.0)
maintenance_cost = st.sidebar.slider("Phần trăm bảo trì (%/năm)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)
monthly_maintenance = equipment_cost * (maintenance_cost / 100) / 12

total_investment = equipment_cost + transformer_cost

st.sidebar.header("Thông số nâng cao")
aux_restroom = st.sidebar.checkbox("Nhà vệ sinh", value=True)
aux_waste = st.sidebar.checkbox("Hệ thống xử lý rác", value=True)
aux_solar = st.sidebar.checkbox("Điện mặt trời áp mái", value=True)
auxiliary = {"restroom": aux_restroom, "waste_management": aux_waste, "solar_installation": aux_solar}

financials = ChargingStationFinancials("vinfast-chargers.json")
validator = StationValidator("vinfast-chargers.json")

revenue_info = financials.calculate_monthly_revenue(
    charger_configs=charger_configs,
    daily_vehicles_per_charger=daily_vehicles,
    avg_charge_time=avg_charge_time,
    peak_hour_ratio=0.3,
    growth_rate=growth_rate,
    location_factor=location_factor,
    additional_services=additional_services
)

operating_costs = OperatingCosts(
    land_lease_per_m2=land_cost,
    staff=staff_cost,
    maintenance=monthly_maintenance * 12,
    other=other_expenses
)

# Giả sử diện tích cần thiết tính từ hàm calculate_required_area trong core.py
required_area = financials.calculate_required_area(charger_configs, mounting_type="wall")
payback_info = financials.calculate_payback_period(
    investment=total_investment,
    monthly_revenue=revenue_info['total_revenue'] * 1_000_000,
    operating_costs=operating_costs,
    required_area=required_area
)
roi = financials.calculate_roi(
    investment=total_investment,
    monthly_revenue=revenue_info['total_revenue'] * 1_000_000,
    operating_costs=operating_costs,
    required_area=required_area
)
annual_report = financials.generate_annual_report(revenue_info['monthly_revenues'])
optimal_poles = financials.suggest_optimal_pole_count(daily_vehicles, charger_configs)
sensitivity = financials.calculate_sensitivity_analysis(
    charger_configs=charger_configs,
    daily_vehicles_per_charger=daily_vehicles,
    avg_charge_time=avg_charge_time,
    peak_hour_ratio=0.3,
    charging_price=financials.electricity_pricing.peak,
    electricity_cost=financials.electricity_pricing.normal,
    growth_rate=growth_rate,
    location_factor=location_factor,
    additional_services=additional_services
)

validation_results = validator.validate_charger_configuration(charger_configs, mounting_type="wall", auxiliary=auxiliary)

st.header("Kết Quả Dự Đoán")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Tổng vốn đầu tư", f"{total_investment/1_000_000_000:.2f} tỷ VND")
    st.metric("Doanh thu tháng", f"{revenue_info['total_revenue']:.2f} triệu VND")
with col2:
    st.metric("Lợi nhuận tháng", f"{payback_info['monthly_profit']:.2f} triệu VND")
    st.metric("ROI", f"{roi:.2f}%")
with col3:
    if payback_info['payback_years'] == float('inf'):
        st.metric("Thời gian hoàn vốn", "Không hoàn vốn")
    else:
        st.metric("Thời gian hoàn vốn", f"{payback_info['payback_years']:.2f} năm")

st.header("Báo cáo tài chính hàng năm")
df_report = pd.DataFrame(annual_report)
st.dataframe(df_report)

st.header("Phân tích độ nhạy")
st.subheader("Phân tích theo lưu lượng xe")
df_sensitivity_traffic = pd.DataFrame(sensitivity['traffic_analysis'])
st.dataframe(df_sensitivity_traffic)
st.subheader("Phân tích theo giá sạc")
df_sensitivity_price = pd.DataFrame(sensitivity['price_analysis'])
st.dataframe(df_sensitivity_price)
st.subheader("Phân tích theo giá điện đầu vào")
df_sensitivity_elec = pd.DataFrame(sensitivity['electricity_cost_analysis'])
st.dataframe(df_sensitivity_elec)

st.header("Phân tích cấu hình trạm sạc")
space_val = validation_results['space_validation']
safety_val = validation_results['safety_validation']
aux_val = validation_results['auxiliary_validation']
power_req = validation_results['power_requirements']
st.subheader("Yêu cầu về không gian")
st.write(space_val)
st.subheader("Yêu cầu về an toàn và hệ thống làm mát")
st.write(safety_val)
st.subheader("Yêu cầu phụ trợ")
st.write(aux_val)
st.subheader("Yêu cầu về công suất")
st.write(power_req)
if validation_results['warnings']:
    st.warning(validation_results['warnings'])

st.header("Khuyến nghị")
st.write(f"Số lượng trụ tối ưu: {optimal_poles}")
