Project Brief: VinFast Charging Station Investment Analysis Tool
Overview
The VinFast Charging Station Investment Analysis Tool is a decision-support application designed to evaluate the financial viability of investing in a VinFast franchised electric vehicle (EV) charging station. This tool enables both technical and non-technical users, including potential investors, to assess costs, revenue, profits, risks, and payback periods for a charging station under VinFast's franchise model. It supports multiple investors (up to 4-5) and provides transparency through detailed financial projections and investor-specific reports.

Non-Technical Summary
Purpose
The tool helps individuals or groups considering investment in a VinFast EV charging station to:

Estimate the initial investment and ongoing operational costs.
Project monthly and annual profits based on VinFast’s profit-sharing model (750 VNĐ/kWh).
Understand profit distribution among multiple investors based on their percentage contributions.
Evaluate risks, such as delayed electricity reimbursements or investor withdrawal.
Determine how long it takes to recover the investment, including loan repayments for borrowed capital.

Key Features

User-Friendly Interface: An interactive dashboard (built with Streamlit) allows users to input parameters like the number of chargers, investor contributions, and operational costs, with real-time results.
Multi-Investor Support: Calculates how costs and profits are split among 1-5 investors based on their percentage contributions to the total investment. For each investor, it shows:
The monetary amount they contribute based on their percentage.
The split between their own (available) capital and borrowed capital.
Monthly profit shares and loan repayment obligations.


Risk Analysis: Visualizes scenarios (optimistic, cautious, high-risk) to show how profits vary under different conditions.
Profit Sharing Reports: Generates clear reports for each investor, detailing their contribution, profit share, loan repayments, and risks.
Flexible Inputs: Adjust settings like land lease costs, loan terms, daily vehicle traffic, and investor-specific parameters to fit specific scenarios.

Benefits

For Investors: Provides clear financial projections, including personalized profit and loan repayment schedules, to make informed decisions.
For Non-Technical Users: Simplifies complex financial analysis with an intuitive interface, no coding or finance expertise required.
For Teams: Ensures fair and transparent profit distribution among multiple investors, minimizing disputes by showing exact contributions and returns.

Use Case Example
A group of 4 investors wants to open a charging station with a total investment of 2.87 billion VNĐ (for 6 chargers, 120kW each). They input:

Investor Contributions:
Investor A: 40% (1.148 billion VNĐ, 80% own capital, 20% borrowed).
Investor B: 30% (0.861 billion VNĐ, 100% own capital).
Investor C: 20% (0.574 billion VNĐ, 50% own capital, 50% borrowed).
Investor D: 10% (0.287 billion VNĐ, 70% own capital, 30% borrowed).


Other Parameters: Land lease costs, expected daily vehicles (e.g., 100), and loan terms (e.g., 10% annual interest, 5-year term).The tool calculates:
Total Investment: 2.87 billion VNĐ.
Monthly Profit: 27.5-93.75 million VNĐ, split by percentage (e.g., Investor A gets 40% of profits).
Loan Repayments: For each investor’s borrowed portion (e.g., Investor A pays ~0.48 million VNĐ/month for 229.6 million VNĐ borrowed).
Payback Period: 2.6-8.7 years, adjusted for loan interest.
Risks: Potential delays in electricity reimbursement or low vehicle traffic.


Technical Summary
Objective
Develop a Python-based application to model the financial performance of a VinFast franchised EV charging station, incorporating VinFast-specific constraints (e.g., electricity prepayment, profit-sharing) and supporting a percentage-based multi-investor model with detailed loan calculations.
Technology Stack

Language: Python 3.11+
Framework: Streamlit for the interactive web interface.
Libraries:
pandas: Data manipulation and investor-specific calculations.
plotly: Interactive visualizations (charts, risk scenarios, investor reports).
json: Configuration file parsing.


Development Environment: Dockerized with VS Code Dev Containers for consistent setup.
Configuration Files:
vinfast-charger.json: Charger specifications.
vinfast-cars.json: Vehicle data (battery capacity, consumption).
time-charge.json: Electricity pricing and time schedules.
investors.json (proposed): Investor contribution and loan details.



System Architecture

Frontend: Streamlit dashboard with sliders, number inputs, and dropdowns for user interaction, displaying metrics (investment, revenue, profit, investor shares) and charts.
Backend: Modular Python codebase in the financial/ directory:
core.py: Financial calculations (investment, revenue, payback, risk, investor shares).
validation.py: Space and safety requirement checks.


Data Flow:
Users input total investment, number of investors, and each investor’s percentage contribution, own capital percentage, and loan terms.
Backend processes inputs using predefined models (ChargingStationFinancials, LoanTerms, InvestorConfig).
Results are visualized in tables, charts, and downloadable investor-specific reports.



Key Functionalities

Investment Calculation: Computes total initial costs (chargers, transformers, construction, land deposit) using a benchmark of 9 million VNĐ/kWh capacity.
Revenue Modeling: Calculates monthly revenue from VinFast’s 750 VNĐ/kWh share, with support for future price adjustments post-2027.
Multi-Investor Logic:
Percentage-Based Contributions: Users specify the total investment and each investor’s contribution as a percentage (summing to 100%). The system calculates the monetary amount each investor contributes.
Own vs. Borrowed Capital: For each investor, users input the percentage of their contribution that is own capital (available funds) and borrowed capital (loan). The system calculates:
Own capital amount (e.g., 80% of 1.148 billion VNĐ = 918.4 million VNĐ).
Borrowed amount (e.g., 20% of 1.148 billion VNĐ = 229.6 million VNĐ).


Profit Sharing: Distributes monthly profits based on each investor’s contribution percentage (e.g., 40% of 50 million VNĐ profit = 20 million VNĐ for Investor A).
Loan Repayments: Calculates monthly loan repayments for each investor’s borrowed portion, using individual loan terms (e.g., principal, interest rate, term).
Investor Reports: Generates reports showing each investor’s contribution, profit share, loan repayment schedule, and net monthly cash flow (profit minus loan repayment).


Electricity Prepayment: Models working capital needs for prepaying electricity costs (up to 1 billion VNĐ/month), with reimbursement delays (15+ days).
Risk Analysis: Simulates scenarios (e.g., low traffic, delayed reimbursements) and supports Monte Carlo analysis for robust risk assessment.
Report Generation: Exports investor-specific reports in PDF/Excel formats, including contribution details, profit shares, loan repayments, and risk scenarios.

Implementation Details for Multi-Investor Model
To support the new multi-investor requirements, the following enhancements are proposed:
Data Model

InvestorConfig Dataclass (new, in financial/core.py):
@dataclass
class InvestorConfig:
    name: str
    contribution_percent: float  # Percentage of total investment (0-100)
    own_capital_percent: float  # Percentage of contribution that is own capital (0-100)
    loan_terms: Optional[LoanTerms]  # Loan details for borrowed portion


Stores each investor’s name, contribution percentage, own capital percentage, and loan terms (if applicable).
Example: InvestorConfig(name="Investor A", contribution_percent=40, own_capital_percent=80, loan_terms=LoanTerms(principal=229_600_000, annual_rate=0.10, term_months=60)).


Validation:

Ensure the sum of contribution_percent across all investors equals 100%.
Validate own_capital_percent is between 0 and 100.
Check that loan terms are provided if own_capital_percent < 100.



User Interface (Streamlit, sample.py)

Total Investment Input:
Add a number input for the total investment amount (e.g., 2.87 billion VNĐ).
Display the calculated total from calculate_total_investment as a reference.


Investor Inputs:
Add a dynamic form for 1-5 investors, where users specify:
Investor name (text input).
Contribution percentage (slider, 0-100%).
Own capital percentage (slider, 0-100%).
Loan terms for borrowed portion (interest rate, term in years).


Real-time display of:
Contribution amount (e.g., 40% of 2.87 billion VNĐ = 1.148 billion VNĐ).
Own capital amount (e.g., 80% of 1.148 billion VNĐ = 918.4 million VNĐ).
Borrowed amount (e.g., 20% of 1.148 billion VNĐ = 229.6 million VNĐ).


Validation to ensure contribution percentages sum to 100%.


Output Display:
Table showing each investor’s:
Contribution amount and percentage.
Own and borrowed capital amounts.
Monthly profit share.
Monthly loan repayment (if applicable).
Net monthly cash flow (profit share minus loan repayment).





Backend Calculations

New Functions (in financial/core.py):
calculate_investor_shares:
Input: List of InvestorConfig, total investment, monthly profit.
Output: Dictionary with each investor’s contribution amount, profit share, and loan details.
Calculation:
Contribution amount = total_investment * contribution_percent / 100.
Own capital = contribution_amount * own_capital_percent / 100.
Borrowed amount = contribution_amount * (100 - own_capital_percent) / 100.
Profit share = monthly_profit * contribution_percent / 100.




calculate_investor_loan_payments:
Input: InvestorConfig with loan terms.
Output: Monthly repayment amount and schedule for the borrowed portion.
Uses calculate_loan_payments logic for each investor’s loan.


generate_investor_report:
Input: Investor shares, loan payments, risk scenarios.
Output: Structured data for PDF/Excel export, including contribution, profit, loan repayments, and net cash flow.




Integration:
Update calculate_payback_period to account for individual loan repayments in the payback calculation.
Update calculate_risk_metrics to include investor-specific risks (e.g., higher loan interest rates impacting net cash flow).



Example Calculation
For a 2.87 billion VNĐ investment, 50 million VNĐ monthly profit, and 4 investors:

Investor A: 40% contribution (1.148 billion VNĐ), 80% own capital (918.4 million VNĐ), 20% borrowed (229.6 million VNĐ, 10% interest, 5-year loan).
Profit share: 40% of 50 million VNĐ = 20 million VNĐ/month.
Loan repayment: ~0.48 million VNĐ/month (calculated via amortization).
Net cash flow: 20 - 0.48 = 19.52 million VNĐ/month.


Investor B: 30% contribution (861 million VNĐ), 100% own capital.
Profit share: 30% of 50 million VNĐ = 15 million VNĐ/month.
Loan repayment: 0 VNĐ.
Net cash flow: 15 million VNĐ/month.


Investor C: 20% contribution (574 million VNĐ), 50% own capital (287 million VNĐ), 50% borrowed (287 million VNĐ).
Profit share: 20% of 50 million VNĐ = 10 million VNĐ/month.
Loan repayment: ~0.60 million VNĐ/month.
Net cash flow: 10 - 0.60 = 9.40 million VNĐ/month.


Investor D: 10% contribution (287 million VNĐ), 70% own capital (200.9 million VNĐ), 30% borrowed (86.1 million VNĐ).
Profit share: 10% of 50 million VNĐ = 5 million VNĐ/month.
Loan repayment: ~0.18 million VNĐ/month.
Net cash flow: 5 - 0.18 = 4.82 million VNĐ/month.



Storage

Option 1: Store investor data in a new investors.json file, loaded at runtime.
Option 2: Store dynamically in memory via Streamlit session state, persisted only during the session.
Recommendation: Use investors.json for persistence and easier integration with reports.

Current Limitations

Electricity Prepayment: Lacks detailed modeling of working capital and delay risks.
Operational Costs: Missing legal/licensing costs.
Revenue Flexibility: Fixed 750 VNĐ/kWh rate, no support for post-2027 changes or free charging until 2027.
Data Integration: Relies on manual input for vehicle traffic, no real-time data from V-Green.
Multi-Investor Logic: Current codebase lacks any investor-specific calculations or UI inputs.

Proposed Enhancements

New Functions (updated to include multi-investor support):
calculate_investor_shares: Distribute costs/profits based on percentage contributions.
calculate_investor_loan_payments: Calculate loan repayments for each investor’s borrowed capital.
generate_investor_report: Create detailed investor reports with contribution, profit, and loan details.
simulate_capital_withdrawal: Model impact of investor withdrawal.
estimate_electricity_cost: Calculate prepaid electricity costs.


Improvements to Existing Functions:
Update calculate_total_investment to include auxiliary costs (e.g., cabinets, signage).
Enhance calculate_risk_metrics with scenarios for withdrawal, electricity price fluctuations, and loan interest rate changes.
Adjust calculate_required_area for complex layouts and safety spacing.
Modify calculate_payback_period to incorporate investor-specific loan repayments.


UI Enhancements:
Add dynamic investor input forms with real-time contribution and loan calculations.
Include validation for contribution percentages and loan terms.
Display investor-specific metrics in a table and charts.



Development Roadmap

Phase 1: Implement multi-investor logic, including InvestorConfig, percentage-based contributions, and loan calculations.
Phase 2: Add investor-specific UI inputs and report generation.
Phase 3: Enhance risk analysis with investor-specific scenarios and integrate real-time traffic data.
Phase 4: Deploy as a cloud-based service with user authentication and persistent investor data.


Target Audience

Non-Technical: Investors, entrepreneurs, or small business owners exploring EV charging opportunities, seeking clear financial insights and personalized profit/loan projections.
Technical: Developers, data analysts, or financial modelers looking to extend the tool with custom features or integrations.

Getting Started

Clone the repository: git clone https://github.com/manhhungdt06/vinfast-charging-station.git.
Install dependencies: pip install -r requirements.txt.
Run the app: streamlit run sample.py.
Access the dashboard at http://localhost:8501 and input parameters, including investor contributions, to analyze.

Contact
For inquiries, contact manhhungdt06@example.com or file an issue on GitHub.
