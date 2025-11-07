# Implementation Plan: Transcription Testing Suite

**Branch**: `2-transcription-testing-suite` | **Date**: 2025-11-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/2-transcription-testing-suite/spec.md`

## Summary

Create comprehensive testing infrastructure to ensure reliable audio saving, accurate transcription, and confident validation of all bot capabilities. Testing includes automated tests for audio file integrity, transcription accuracy (word-level alignment and speaker diarization), schema validation, and manual review procedures. Uses existing Python/pytest infrastructure without introducing new technologies.

## Technical Context

**Language/Version**: Python 3.7+  
**Primary Dependencies**: pytest, existing bot dependencies (discord.py, whisperx, torch)  
**Storage**: Filesystem (test audio fixtures, expected outputs, test results)  
**Testing**: pytest with fixtures and parameterized tests  
**Target Platform**: Same as main bot (server with optional GPU support)  
**Project Type**: single (testing module within existing bot project)  
**Performance Goals**: Tests complete in <5 minutes total; transcription accuracy >95%  
**Constraints**: Must not require manual intervention for CI/CD; must work offline with test fixtures  
**Scale/Scope**: Cover all bot commands and workflows; provide sample test audio for common scenarios

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Simplicity & Extensibility**: Tests follow standard pytest patterns; easy to add new test cases
- **Session-End Audio Transcription**: Tests verify session recording and batch transcription workflow
- **Thread-Safe, Guild-Isolated Operation**: Tests validate per-guild state isolation
- **Structured Logging & Observability**: Tests verify JSON logging format and completeness
- **Player Mapping & Dynamic Configuration**: Tests validate YAML mapping and updates
- **Additional Constraints**: Uses Python 3.7+, pytest, no new dependencies beyond testing libraries

## Project Structure

### Documentation (this feature)

```text
specs/2-transcription-testing-suite/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (test API if needed)
└── checklists/          # Spec quality checklist
```

### Source Code (repository root)

```text
tests/
├── fixtures/
│   ├── audio/
│   │   ├── single_speaker_10s.wav
│   │   ├── multi_speaker_30s.wav
│   │   └── corrupted.wav
│   ├── metadata/
│   │   ├── valid_metadata.json
│   │   └── malformed_metadata.json
│   └── expected_outputs/
│       ├── single_speaker_transcript.json
│       └── multi_speaker_transcript.json
├── test_audio_saving.py
├── test_transcription.py
├── test_schema_validation.py
├── test_bot_commands.py
├── conftest.py
└── README.md

src/
├── transcription/
│   └── (existing modules)
└── testing/
    ├── __init__.py
    ├── test_helpers.py
    └── validators.py
```

**Structure Decision**: Single project testing module. Tests live in `tests/` directory following pytest conventions. Test fixtures (sample audio, metadata, expected outputs) stored in `tests/fixtures/`. Helper utilities in `src/testing/` for reusable validation logic.

## Complexity Tracking

> No Constitution Check violations. All gates justified and aligned with project principles.
