# Project Brief: VinFast Charging Station Investment Analysis Tool

## Overview
The VinFast Charging Station Investment Analysis Tool is a decision-support application designed to evaluate the financial viability of investing in a VinFast franchised electric vehicle (EV) charging station. This tool enables both technical and non-technical users, including potential investors, to assess costs, revenue, profits, risks, and payback periods for a charging station under VinFast's franchise model. It supports multiple investors (up to 4-5) and provides transparency through detailed financial projections and investor-specific reports.

---

## Non-Technical Summary

### Purpose
The tool helps individuals or groups considering investment in a VinFast EV charging station to:
- Estimate the initial investment and ongoing operational costs.
- Project monthly and annual profits based on VinFast’s profit-sharing model (750 VNĐ/kWh).
- Understand profit distribution among multiple investors.
- Evaluate risks, such as delayed electricity reimbursements or investor withdrawal.
- Determine how long it takes to recover the investment.

### Key Features
- **User-Friendly Interface**: An interactive dashboard (built with Streamlit) allows users to input parameters like the number of chargers, investor contributions, and operational costs, with real-time results.
- **Multi-Investor Support**: Calculates how costs and profits are split among 1-5 investors, ensuring transparency.
- **Risk Analysis**: Visualizes scenarios (optimistic, cautious, high-risk) to show how profits vary under different conditions.
- **Profit Sharing Reports**: Generates clear reports for each investor, detailing their share of profits and risks.
- **Flexible Inputs**: Adjust settings like land lease costs, loan terms, and daily vehicle traffic to fit specific scenarios.

### Benefits
- **For Investors**: Provides clear financial projections to make informed decisions, reducing uncertainty in a complex investment.
- **For Non-Technical Users**: Simplifies financial analysis with an intuitive interface, no coding or finance expertise required.
- **For Teams**: Supports group investments by ensuring fair profit distribution and transparency, minimizing disputes.

### Use Case Example
A group of 4 investors wants to open a charging station with 6 chargers (120kW each). They input their capital contributions, land lease costs, and expected daily vehicles (e.g., 100). The tool calculates:
- Total investment: ~2.87 billion VNĐ.
- Monthly profit: ~27.5-93.75 million VNĐ, split by investor shares.
- Payback period: 2.6-8.7 years.
- Risks: Potential delays in electricity reimbursement or low vehicle traffic.

---

## Technical Summary

### Objective
Develop a Python-based application to model the financial performance of a VinFast franchised EV charging station, incorporating VinFast-specific constraints (e.g., electricity prepayment, profit-sharing) and supporting multiple investors.

### Technology Stack
- **Language**: Python 3.11+
- **Framework**: Streamlit for the interactive web interface.
- **Libraries**:
  - `pandas`: Data manipulation and analysis.
  - `plotly`: Interactive visualizations (charts, risk scenarios).
  - `json`: Configuration file parsing.
- **Development Environment**: Dockerized with VS Code Dev Containers for consistent setup.
- **Configuration Files**:
  - `vinfast-charger.json`: Charger specifications.
  - `vinfast-cars.json`: Vehicle data (battery capacity, consumption).
  - `time-charge.json`: Electricity pricing and time schedules.

### System Architecture
- **Frontend**: Streamlit dashboard with sliders, number inputs, and dropdowns for user interaction, displaying metrics (investment, revenue, profit) and charts.
- **Backend**: Modular Python codebase in the `financial/` directory:
  - `core.py`: Financial calculations (investment, revenue, payback, risk).
  - `validation.py`: Space and safety requirement checks.
- **Data Flow**:
  - Users input parameters (e.g., charger types, investor shares, vehicle traffic).
  - Backend processes inputs using predefined models (`ChargingStationFinancials`, `LoanTerms`).
  - Results are visualized in tables, charts, and downloadable reports.

### Key Functionalities
- **Investment Calculation**: Computes total initial costs (chargers, transformers, construction, land deposit) using a benchmark of 9 million VNĐ/kWh capacity.
- **Revenue Modeling**: Calculates monthly revenue from VinFast’s 750 VNĐ/kWh share, with support for future price adjustments post-2027.
- **Multi-Investor Logic**: Distributes costs and profits based on each investor’s capital contribution, with safeguards against withdrawal risks.
- **Electricity Prepayment**: Models working capital needs for prepaying electricity costs (up to 1 billion VNĐ/month), with reimbursement delays (15+ days).
- **Risk Analysis**: Simulates scenarios (e.g., low traffic, delayed reimbursements) and supports Monte Carlo analysis for robust risk assessment.
- **Report Generation**: Exports investor-specific reports in PDF/Excel formats.

### Current Limitations
- **Electricity Prepayment**: Lacks detailed modeling of working capital and delay risks.
- **Operational Costs**: Missing power capacity fees, insurance, and marketing costs.
- **Revenue Flexibility**: Fixed 750 VNĐ/kWh rate, no support for post-2027 changes.
- **Data Integration**: Relies on manual input for vehicle traffic, no real-time data from V-Green.

### Proposed Enhancements
- **New Functions**:
  - `calculate_investor_shares`: Distribute costs/profits among investors.
  - `simulate_capital_withdrawal`: Model impact of investor withdrawal.
  - `estimate_electricity_cost`: Calculate prepaid electricity costs.
  - `generate_investor_report`: Create detailed investor reports.
- **Improvements to Existing Functions**:
  - Update `calculate_total_investment` to include auxiliary costs (e.g., cabinets, signage).
  - Enhance `calculate_risk_metrics` with scenarios for withdrawal and electricity price fluctuations.
  - Adjust `calculate_required_area` for complex layouts and safety spacing.

### Development Roadmap
- **Phase 1**: Implement multi-investor logic and electricity prepayment modeling.
- **Phase 2**: Add advanced risk analysis (Monte Carlo, competitive density).
- **Phase 3**: Integrate real-time traffic data and support independent station modeling.
- **Phase 4**: Deploy as a cloud-based service with user authentication.

---

## Target Audience
- **Non-Technical**: Investors, entrepreneurs, or small business owners exploring EV charging opportunities, seeking clear financial insights.
- **Technical**: Developers, data analysts, or financial modelers looking to extend the tool with custom features or integrations.

## Getting Started
1. Clone the repository: `git clone https://github.com/manhhungdt06/vinfast-charging-station.git`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run the app: `streamlit run sample.py`.
4. Access the dashboard at `http://localhost:8501` and input parameters to analyze.

## Contact
For inquiries, contact [manhhungdt06@example.com](mailto:manhhungdt06@example.com) or file an issue on GitHub.