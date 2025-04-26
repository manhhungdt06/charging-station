# System Architecture Patterns

## Financial Module Patterns:
1. **Working Capital Management**:
   - Electricity prepayment modeled as working capital requirement
   - Configurable months of prepayment
   - Opportunity cost calculation based on loan terms

2. **Cost Calculation**:
   - Layered cost structure (base + capacity + insurance + marketing)
   - Transformer costs calculated per kW
   - Error margin built into total investment

3. **Revenue Modeling**:
   - Fixed owner share per kWh
   - Overage fee calculation
   - Time-based revenue tracking

## Validation Patterns:
1. **Safety Requirements**:
   - Mandatory safety features (emergency stop, fault protection)
   - Configurable IP ratings
   - Certified equipment flagging

2. **Space Calculation**:
   - Mounting-type specific spacing
   - Safety margin application
   - Area breakdowns (parking/transformer/auxiliary)

## Technical Patterns:
1. **Backward Compatibility**:
   - Default parameters for new features
   - Optional new parameters
   - Deprecation warnings for old patterns

2. **Type Safety**:
   - Complete type hints
   - Data classes for configurations
   - Validation decorators
