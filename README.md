# VinFast Charging Station Investment Analysis

## Overview
This project provides a comprehensive tool to analyze the financial viability of investing in a VinFast franchised electric vehicle (EV) charging station. Built using Python and Streamlit, it allows users to input various parameters, calculate costs, revenue, profit, and payback period, and assess risks associated with the investment. The tool is designed to support multiple investors (up to 4-5) and accounts for unique aspects of the VinFast franchise model, such as electricity cost prepayment and profit-sharing.

## Features
- **Investment Cost Calculation**: Estimates total initial investment, including chargers, transformers, construction, and auxiliary costs.
- **Revenue Projection**: Calculates monthly revenue based on VinFast's profit-sharing model (750 VNĐ/kWh) and additional income sources.
- **Profit Sharing**: Supports multiple investors by calculating individual shares of costs, revenue, and profits.
- **Risk Analysis**: Evaluates scenarios like capital withdrawal, delayed electricity reimbursement, and fluctuating vehicle traffic.
- **Payback Period**: Determines the time required to recover the investment, considering operational costs and loan terms.
- **Interactive Dashboard**: Streamlit-based UI for real-time input adjustments and visualizations (charts, risk scenarios).
- **Investor Reports**: Generates detailed reports for each investor, enhancing transparency and commitment.

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/manhhungdt06/vinfast-charging-station.git
   cd vinfast-charging-station
   ```
2. **Install Dependencies**:
   Ensure Python 3.11+ is installed, then run:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Application**:
   ```bash
   streamlit run sample.py
   ```
   The app will open in your browser at `http://localhost:8501`.

## Usage
1. **Configure Parameters**:
   - Select charger types and quantities (e.g., 120kW DC chargers).
   - Input number of investors and their capital contributions.
   - Adjust operational costs (land lease, staff, maintenance, etc.).
   - Set loan terms, electricity prepayment periods, and additional income.
2. **Analyze Results**:
   - View total investment, monthly revenue, profit, and payback period.
   - Check profit distribution among investors.
   - Explore risk scenarios (optimistic, cautious, high-risk).
3. **Generate Reports**:
   - Export detailed investor reports as PDF or Excel for transparency.

## Project Structure
```
vinfast-charging-station/
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
├── sample.py               # Main Streamlit application
├── time-charge.json        # Electricity pricing and time schedules
├── vinfast-cars.json       # VinFast vehicle specifications
├── vinfast-charger.json    # Charger configurations
├── vinfast-chargers.json   # Duplicate charger data (to be merged)
├── financial/              # Financial calculation modules
│   ├── __init__.py
│   ├── core.py            # Core financial calculations
│   └── validation.py       # Validation for space and safety
└── .devcontainer/          # Dev container configuration
    └── devcontainer.json
```

## Key Assumptions
- **Electricity Costs**: Partners prepay electricity costs to EVN within 10 days, with VinFast reimbursing after 15 days (subject to delays).
- **Profit Sharing**: VinFast pays 750 VNĐ/kWh, fixed for 10 years, with potential adjustments post-2027.
- **Investment Model**: Supports 1-5 investors, with customizable capital contributions and profit splits.
- **Charging Demand**: Based on 100-150 vehicles/day per station, adjustable via user input.
- **Initial Investment**: Guided by a benchmark of 9 million VNĐ/kWh of total station capacity.

## Limitations and Future Improvements
- **Electricity Prepayment**: Enhance modeling of working capital needs for electricity prepayments.
- **Operational Costs**: Add support for power capacity fees, insurance, and marketing costs.
- **Revenue Flexibility**: Incorporate post-2027 revenue changes and market-based pricing for comparison with independent stations.
- **Risk Analysis**: Expand scenarios to include electricity price fluctuations and competitive station density.
- **Data Integration**: Integrate real-time vehicle traffic data from V-Green for accurate demand forecasting.

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit changes (`git commit -m 'Add YourFeature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a Pull Request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For questions or feedback, contact the project maintainer at [manhhungdt06@example.com](mailto:manhhungdt06@example.com) or open an issue on GitHub.