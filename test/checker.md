```mermaid
flowchart TD
    A[User Input Parameters] --> B[Charger Configuration]
    A --> C[Land Cost per m²]
    A --> D[Mounting Type]
    A --> E[Loan Terms]
    A --> F[Daily Vehicles per Pole]
    A --> G[Operation Cost]
    
    B --> H[Calculate Equipment Cost]
    B --> I[Calculate Total Power]
    I --> J{Transformer Needed?}
    J -->|Yes| K[Add Transformer Cost]
    J -->|No| L[Proceed]
    
    B --> M[Calculate Required Area]
    D --> M
    M --> N[Monthly Land Cost]
    
    H --> O[Total Investment Cost]
    K --> O
    N --> O
    
    F --> P[Calculate Monthly Revenue]
    B --> P
    P --> Q[Base Revenue + Subsidy]
    
    G --> R[Operating Costs]
    N --> R
    E --> S[Calculate Loan Payments]
    S --> T[Monthly Loan Cost]
    
    Q --> U[Calculate Payback Period]
    R --> U
    T --> U
    O --> U
    
    U --> V[Monthly Profit]
    U --> W[Payback Years]
    
    P --> X[Risk Analysis]
    R --> X
    X --> Y[Scenario Results]
    
    V --> Z[Display Metrics]
    W --> Z
    Y --> Z
    Z --> AA[Output Charts]
    
    subgraph Inputs
        A
    end
    
    subgraph Calculations
        H
        I
        J
        K
        M
        P
        Q
        R
        S
        U
        X
    end
    
    subgraph Outputs
        Z
        AA
    end
```

### Key Components:
1. **Input Parameters**:
   - Charger types/quantities
   - Land cost, mounting type
   - Loan terms (amount, rate, duration)
   - Operation costs
   - Daily vehicle traffic

2. **Core Calculations**:
   - **Equipment Costs**: Sum of charger costs + transformer (if power >560kW)
   - **Space Requirements**: Calculated based on mounting type and charger quantities
   - **Revenue Model**: 
     - Energy consumption × electricity pricing
     - Government subsidies
   - **Loan Amortization**: Monthly payment calculations
   - **Payback Analysis**: 
     ```python
     (Total Investment) / (Monthly Revenue - Operating Costs - Loan Payments)
     ```
   - **Risk Scenarios**: Sensitivity analysis with ±20% revenue/cost variations

3. **Outputs**:
   - Key metrics: Total investment, monthly profit, payback period
   - Visualizations: 
     - Cumulative profit vs time chart
     - Risk scenario comparison bars
   - Validation alerts: Space requirements, safety compliance

4. **Data Flow**:
   User inputs → Configuration validation → Financial calculations → Risk modeling → Visualization rendering

This flow chart shows how user inputs propagate through different calculation modules to produce both numerical results and visual outputs used for investment decision-making.