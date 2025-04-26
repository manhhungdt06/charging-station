# Technical Context

## Core Technologies
- **Streamlit**: Chosen for rapid development of financial dashboards
- **Plotly**: Enables interactive visualization of risk scenarios
- **Pandas**: Handles financial calculations and data transformations

## Key Components
1. `financial/core.py` - Core financial models:
   - ChargingStationFinancials class
   - LoanTerms calculations
   - Risk scenario modeling

2. `financial/validation.py` - Business rule validation:
   - Space requirements
   - Safety regulations
   - Investor allocation rules

3. Configuration files:
   - `vinfast-charger.json`: Technical specs
   - `vinfast-cars.json`: Vehicle data
   - `time-charge.json`: Electricity pricing

## Architectural Patterns
- **Modular Design**: Separates financial logic from UI
- **Data-Driven**: Configuration files enable scenario testing
- **Reactive UI**: Streamlit updates calculations in real-time

## Technical Constraints
- Must support non-technical users through simple UI
- Calculations must match VinFast's financial models exactly
- Needs to handle Vietnamese currency formatting
- Must work offline for field use cases

## Development Practices
- Dockerized environment for consistency
- JSON configuration for easy updates
- Type hints for maintainability
- Streamlit caching for performance
