# Research: Transcription Testing Suite

## Decision: Testing Framework
- **Chosen**: pytest with standard fixtures and parameterized tests
- **Rationale**: Already used in Python ecosystem; supports fixtures, parametrization, and CI/CD integration
- **Alternatives considered**: unittest (less flexible), nose2 (less maintained)

## Decision: Test Audio Fixtures
- **Chosen**: Pre-recorded WAV files in tests/fixtures/audio/ covering common scenarios
- **Rationale**: Consistent, reproducible test inputs; no runtime audio generation needed
- **Alternatives considered**: Synthetic audio generation (complex), live Discord sessions (unreliable)

## Decision: Expected Output Format
- **Chosen**: JSON files in tests/fixtures/expected_outputs/ matching actual transcript schema
- **Rationale**: Direct comparison with actual outputs; easy to update when schema changes
- **Alternatives considered**: Hardcoded strings (brittle), dynamic generation (complex)

## Decision: Schema Validation Approach
- **Chosen**: Use existing src/transcription/validator.py for automated schema checks
- **Rationale**: Reuses production validation code; ensures tests match production behavior
- **Alternatives considered**: Separate test-only validator (duplicate logic)

## Decision: Manual Review Process
- **Chosen**: Document manual review steps in quickstart.md with checklists
- **Rationale**: Manual review catches edge cases automation misses; provides human confidence
- **Alternatives considered**: Fully automated (misses subjective quality), no manual process (risky)

## Decision: CI/CD Integration
- **Chosen**: pytest with JUnit XML output for GitHub Actions or similar CI systems
- **Rationale**: Standard CI integration; works offline with fixtures; fast execution
- **Alternatives considered**: Manual testing only (no automation), cloud-based testing (dependency)
