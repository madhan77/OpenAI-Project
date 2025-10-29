# Health Claims Processing Platform

This repository contains a reference implementation of a health claims processing platform that aligns with the product requirements document (PRD) and is ready for formal stakeholder review.

## Features
- Intake, validation, manual review, and auto-adjudication orchestrated by `ClaimsProcessingApp`.
- Modular validators and rules capturing eligibility, documentation, coding, duplicate detection, and policy heuristics.
- Manual review work queue, payment instruction and EOB generation, and multi-channel notifications.
- In-memory repositories and metrics collectors for deterministic tests with clear extension points.

## Getting Started
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt  # if using additional deps
   ```
   *(The core app uses only the Python standard library and `pytest` for tests.)*
2. **Run the test suite**
   ```bash
   pytest
   ```
3. **Explore the workflow**
   - Use the fixtures in `tests/test_claims_processing_app.py` as examples for constructing claims.
   - Instantiate `claims_app.ClaimsProcessingApp` to submit and process claims end to end.

## Documentation
- [PRD](docs/claims-processing-prd.md)
- [Application Architecture](docs/claims-processing-app.md)

## Project Structure
```
claims_app/        # Application modules (workflow, models, validators, rules, etc.)
agents/            # Convenience exports for downstream integrations
docs/              # Product and technical documentation
tests/             # Pytest coverage demonstrating key workflows
```

## Contributing
Contributions should preserve the modular architecture and include pytest coverage for new behaviour. Please update documentation when introducing new workflows or policy rules.
