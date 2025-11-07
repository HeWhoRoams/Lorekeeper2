<!--
Sync Impact Report
Version change: 1.1.0 → 1.2.0
Modified principles: II. Real-Time Voice Transcription → II. Session-End Audio Transcription
Added sections: None
Removed sections: None
Templates requiring updates: ✅ plan-template.md, ✅ spec-template.md, ✅ tasks-template.md
Follow-up TODOs: TODO(RATIFICATION_DATE): Original ratification date unknown, set after confirmation
-->

# V.O.L.O Discord Transcription Bot Constitution

## Core Principles

### I. Simplicity & Extensibility
The bot MUST remain simple to operate, with a clear command structure and minimal configuration.
All features MUST be designed for easy extension, allowing new commands and integrations without major refactoring.
Rationale: Ensures maintainability and rapid feature addition for evolving Discord needs.

### II. Session-End Audio Transcription
The bot MUST reliably join Discord voice channels, record session audio, and transcribe only after the session ends.
Audio MUST be saved during the session and processed in batch at completion, not in real time.
Transcription MUST support multiple speakers and log results in structured, queryable formats.
Rationale: Ensures accurate, multi-user transcription for session archiving and review, while reducing real-time resource requirements.

### III. Thread-Safe, Guild-Isolated Operation
All audio processing MUST be thread-safe and isolated per Discord guild (server).
State (voice clients, sinks, logs) MUST be managed per guild to prevent cross-server interference.
Rationale: Prevents data leaks and ensures robust multi-server operation.

### IV. Structured Logging & Observability
Transcriptions MUST be logged as structured JSON with fields: date, begin, end, user_id, player, character, event_source, data.
Logging MUST support debugging and compliance review. All errors and exceptions MUST be logged with context.
Rationale: Enables auditability and troubleshooting for live deployments.

### V. Player Mapping & Dynamic Configuration
User-to-player/character mapping MUST be maintained in a YAML file, loaded at startup and updatable via bot command.
Configuration changes MUST be reflected without restart when possible.
Rationale: Supports dynamic campaigns and evolving player rosters.

## Additional Constraints

- Python 3.7+ required; dependencies managed via requirements.txt.
- All environment variables (bot token, channel ID, player map path) MUST be set via .env file.
- Audio processing MUST fallback to CPU if GPU VRAM <5GB.
- All commands MUST be async and provide user feedback on long operations.

## Development Workflow

- All new features and bug fixes MUST be submitted via pull request and reviewed for compliance with principles.
- Code reviews MUST verify thread safety, logging, and extensibility.
- Manual testing required for audio features; automated tests for non-audio logic encouraged.
- Versioning follows semantic rules: MAJOR for breaking changes, MINOR for new principles/sections, PATCH for clarifications.

## Governance

- This constitution supersedes all other development practices for the V.O.L.O bot.
- Amendments require documentation, approval, and migration plan.
- All PRs/reviews MUST verify compliance with principles and constraints.
- Complexity MUST be justified in PRs and tracked in plan/spec templates.
- Use `.github/copilot-instructions.md` for runtime development guidance.

**Version**: 1.2.0 | **Ratified**: TODO(RATIFICATION_DATE): original date unknown | **Last Amended**: 2025-11-06
