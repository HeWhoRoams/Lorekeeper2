# Feature Specification: Audio Transcription

**Feature Branch**: `1-audio-transcription`  
**Created**: 2025-11-06  
**Status**: Draft  
**Input**: User description: "Transcribe recorded Discord voice session audio into timestamped text using WhisperX, with optional speaker diarization. This module runs after the audio_capture module finishes and saves its artifacts. It loads 'session_audio_16k.wav' and 'metadata.json', performs WhisperX transcription and alignment, and outputs 'transcript.json' containing segments, timestamps, speaker labels, and word-level alignment data. It should run asynchronously to avoid blocking the main Discord bot loop. Inputs: session_audio_16k.wav, metadata.json. Outputs: transcript.json, logs/transcription_[timestamp].log. Acceptance: Transcription completes without runtime errors; word timestamps align within ±250ms of audio playback; diarization (if enabled) assigns speaker labels consistently; transcript.json validates against schema; log includes runtime, model name, and accuracy metrics."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Audio Transcription (Priority: P1)

After a voice session is recorded, the system automatically loads the audio file and metadata, runs WhisperX transcription, and saves a timestamped transcript with word-level alignment data.

**Why this priority**: Core functionality - converting recorded audio to text is the primary value.

**Independent Test**: Provide valid audio and metadata files, verify transcript.json is created with accurate timestamps and text.

**Acceptance Scenarios**:

1. **Given** session_audio_16k.wav and metadata.json exist, **When** transcription starts, **Then** transcript.json is created with segments, timestamps, and text.
2. **Given** transcription completes, **When** timestamps are checked against audio playback, **Then** they align within ±250ms.
3. **Given** transcription runs, **When** it completes, **Then** no runtime errors occur and logs show success.

---

### User Story 2 - Speaker Diarization (Priority: P2)

When diarization is enabled, the system identifies different speakers in the audio and assigns consistent labels to transcript segments.

**Why this priority**: Multi-speaker sessions need speaker attribution for clarity.

**Independent Test**: Record multi-speaker audio, enable diarization, verify speaker labels are assigned consistently.

**Acceptance Scenarios**:

1. **Given** multi-speaker audio and diarization enabled, **When** transcription completes, **Then** transcript.json includes speaker labels for each segment.
2. **Given** the same speaker speaks multiple times, **When** diarization runs, **Then** consistent labels are assigned.

---

### User Story 3 - Asynchronous Processing (Priority: P3)

The transcription runs in the background without blocking the Discord bot's main loop, allowing the bot to continue responding to commands.

**Why this priority**: Ensures bot responsiveness during long transcription operations.

**Independent Test**: Start transcription, verify bot can still respond to commands during processing.

**Acceptance Scenarios**:

1. **Given** transcription is running, **When** a bot command is issued, **Then** the bot responds immediately without waiting for transcription to complete.

---

### Edge Cases

- What happens if audio file is corrupted or missing?
- How does the system handle very long audio files?
- What if WhisperX model fails to load?
- How are transcription errors logged and reported?
- What if metadata.json is malformed?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST load session_audio_16k.wav and metadata.json from the audio_capture output.
- **FR-002**: System MUST run WhisperX transcription on the audio file.
- **FR-003**: System MUST generate transcript.json with segments, timestamps, text, and word-level alignment.
- **FR-004**: System MUST support optional speaker diarization with consistent label assignment.
- **FR-005**: System MUST save transcription logs with runtime, model name, and accuracy metrics.
- **FR-006**: System MUST run transcription asynchronously to avoid blocking the bot.

### Key Entities

- **TranscriptSegment**: Represents a segment of transcribed audio, attributes: start_time, end_time, text, speaker_label, words (with timestamps).
- **TranscriptionLog**: Represents logging data, attributes: timestamp, runtime, model_name, accuracy_metrics, errors.

## Assumptions

- WhisperX is installed and available in the environment.
- Audio files are in the correct 16kHz mono 16-bit PCM WAV format.
- Metadata.json contains valid session information.
- Transcription runs after audio_capture completes successfully.
- Diarization is optional and can be enabled/disabled via configuration.

## Success Criteria

- Transcription completes without runtime errors in 95% of cases.
- Word timestamps align within ±250ms of actual audio playback.
- Speaker diarization assigns consistent labels across segments when enabled.
- Transcript.json validates against a defined JSON schema.
- Logs include runtime duration, WhisperX model name, and accuracy confidence scores.