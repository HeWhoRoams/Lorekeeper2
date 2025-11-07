# Feature Specification: Audio Capture

**Feature Branch**: `1-audio_capture`  
**Created**: 2025-11-06  
**Status**: Draft  
**Input**: User description: "Record voice sessions from a Discord voice channel into 16kHz mono WAV files suitable for WhisperX transcription. The bot connects to a Discord voice channel, records user audio for a fixed duration or until stopped, and saves the audio file along with session metadata (guild, channel, participants, timestamps). Outputs: session_audio_16k.wav, metadata.json. Acceptance: The audio file plays cleanly, meets WhisperX requirements (16kHz, mono, 16-bit PCM), and metadata correctly lists session details and duration."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record Discord Session (Priority: P1)

A user starts a recording session in a Discord voice channel. The bot records all user audio until the session ends or a fixed duration is reached, then saves the audio as a 16kHz mono WAV file and generates session metadata.

**Why this priority**: This is the core value—capturing session audio for later transcription and review.

**Independent Test**: Start a session, end it, and verify the audio file and metadata are created and meet requirements.

**Acceptance Scenarios**:

1. **Given** the bot is connected to a voice channel, **When** a user starts a recording, **Then** the bot records all audio and saves a WAV file and metadata at session end.
2. **Given** a session is in progress, **When** the fixed duration is reached or a user stops the session, **Then** the bot finalizes and saves the audio and metadata.
3. **Given** a completed session, **When** the audio file is played, **Then** it is clean, mono, 16kHz, and suitable for WhisperX transcription.

---

### User Story 2 - Metadata Accuracy (Priority: P2)

The bot generates a metadata file listing guild, channel, participants, start/end timestamps, and session duration.

**Why this priority**: Accurate metadata is essential for organizing and searching session archives.

**Independent Test**: Start and end a session, then verify metadata.json contains correct details.

**Acceptance Scenarios**:

1. **Given** a completed session, **When** metadata.json is inspected, **Then** it lists correct guild, channel, participants, timestamps, and duration.

---

### User Story 3 - Error Handling (Priority: P3)

If audio cannot be recorded or saved, the bot provides a clear error message and does not create incomplete files.

**Why this priority**: Ensures reliability and user trust.

**Independent Test**: Simulate a recording failure and verify error handling and messaging.

**Acceptance Scenarios**:

1. **Given** a recording error occurs, **When** the session ends, **Then** the bot reports the error and does not save partial files.

---

### Edge Cases

- What happens if a user disconnects mid-session?
- How does the system handle multiple users joining/leaving during recording?
- What if the bot loses connection to Discord?
- How are overlapping sessions handled?
- What if the audio format conversion fails?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST record all user audio in a Discord voice channel for a session.
- **FR-002**: System MUST save the audio as a 16kHz mono 16-bit PCM WAV file suitable for WhisperX.
- **FR-003**: System MUST generate a metadata.json file with guild, channel, participants, timestamps, and duration.
- **FR-004**: System MUST handle session start/stop by user command or fixed duration.
- **FR-005**: System MUST provide clear error messages and avoid saving incomplete files.

### Key Entities

- **SessionAudio**: Represents the recorded audio file, attributes: file_path, format, sample_rate, channels, bit_depth, duration.
- **SessionMetadata**: Represents session details, attributes: guild_id, channel_id, participants, start_time, end_time, duration, file_path.

## Assumptions

- WhisperX requires 16kHz mono 16-bit PCM WAV files.
- Bot has permission to join and record in the target voice channel.
- Session duration is either user-controlled or fixed by configuration.
- Metadata is saved as JSON in the same directory as the audio file.

## Success Criteria

- Audio file is playable, mono, 16kHz, 16-bit PCM, and suitable for WhisperX.
- Metadata.json lists correct session details and duration.
- No incomplete or corrupted files are saved.
- Users receive clear feedback on errors or completion.
