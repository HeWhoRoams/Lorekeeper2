# Implementation Plan: audio_capture

**Branch**: `1-audio_capture` | **Date**: 2025-11-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/1-audio_capture/spec.md`

## Summary

Implement, test, and verify the Discord voice recording subsystem per constitution. The bot will record user audio in a Discord voice channel, save it as a 16kHz mono WAV file, and generate session metadata. The plan covers setup, build, validation, refinement, and merge phases, with metrics for audio quality, file integrity, and metadata completeness. Gates include pytest pass, manual validation, and documentation update.

## Technical Context

**Language/Version**: Python 3.7+  
**Primary Dependencies**: py-cord[voice], pyyaml, python-dotenv, reportlab, faster_whisper, speechrecognition, torch  
**Storage**: Filesystem (WAV, JSON)  
**Testing**: pytest, manual playback validation  
**Target Platform**: Discord bot running on Windows/Linux server  
**Project Type**: single (bot + audio subsystem)  
**Performance Goals**: Audio file must be clean, mono, 16kHz, 16-bit PCM; metadata must be complete and accurate  
**Constraints**: Audio format must meet WhisperX requirements; session metadata must be correct; bot must handle errors gracefully  
**Scale/Scope**: Single Discord server, multiple users per session

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Simplicity & Extensibility: Bot design must allow easy extension and configuration
- Session-End Audio Transcription: Audio is saved and processed after session ends, not real-time
- Thread-Safe, Guild-Isolated Operation: All state and audio processing isolated per guild
- Structured Logging & Observability: Transcriptions and errors logged as structured JSON
- Player Mapping & Dynamic Configuration: User mapping via YAML, updatable via command
- Additional Constraints: Python 3.7+, .env config, async commands, CPU fallback, error feedback

## Project Structure

### Documentation (this feature)

```text
specs/1-audio_capture/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── checklists/          # Spec quality checklist
```

### Source Code (repository root)

```text
src/
├── bot/
├── sinks/
├── config/
├── utils/
assets/
```

**Structure Decision**: Single project, bot and audio subsystem in `src/`.

## Complexity Tracking

> No Constitution Check violations. All gates justified and aligned with project principles.
