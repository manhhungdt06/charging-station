# Active Context

## Current Focus Areas
1. **Multi-Investor Logic**:
   - Implementing fair profit distribution calculations
   - Handling investor withdrawal scenarios
   - Visualizing individual investor returns

2. **Electricity Prepayment Modeling**:
   - Working capital requirements
   - Cash flow impact of 15+ day reimbursement delays
   - Risk mitigation strategies

3. **Report Generation**:
   - Investor-specific PDF reports
   - Standardized financial statement formats
   - Vietnamese language support

## Recent Changes
- Added initial multi-investor calculation framework
- Integrated Vietnamese currency formatting
- Created base templates for investor reports
- Added electricity prepayment warning system

## Open Questions
1. How should we handle partial investor withdrawals?
2. What's the optimal way to model electricity price fluctuations post-2027?
3. Should reports include comparative benchmarks?

## Pending Decisions
1. Finalize investor report template design
2. Choose between PDF or Excel as primary report format
3. Determine minimum viable working capital recommendation

## Immediate Next Steps
1. Complete `calculate_investor_shares()` implementation
2. Add withdrawal scenario simulation
3. Prototype PDF report generation
4. Document electricity prepayment assumptions

## Blockers
- Need clarification on VinFast's exact reimbursement timeline
- Awaiting design assets for report templates
- Pending legal review of disclaimer language
