# Technical Implementation Details

## Core Technologies:
- Python 3.10+
- Dataclasses for configuration models
- Type hints throughout codebase
- JSON configuration files

## Key Modules:
1. **Financial Calculations**:
   - `core.py`: Main financial models and calculations
   - `validation.py`: Space and safety requirements
   - Sample data files in JSON format

## Implementation Highlights:

### Electricity Cost Modeling:
```python
# Uses actual EVN rates with owner share
electricity_cost = total_kwh * owner_share_per_kwh
working_capital = electricity_cost * prepayment_months
```

### Safety Requirements:
```python
@dataclass
class SafetyRequirements:
    emergency_stop: bool = True
    ground_fault_protection: bool = True
    temperature_monitoring: bool = True
```

### Space Calculations:
```python
total_width = (parking_width * spots) + 
              (spacing * (spots-1)) + 
              (2 * safety_margin)
```

## Dependencies:
- Standard library only (no external packages)
- JSON config files for charger specifications
- Type checking via Pylance

## Development Practices:
- Strict type checking
- Backward compatibility maintained
- Comprehensive docstrings
- Validation decorators
