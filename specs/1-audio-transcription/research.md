# Research: audio-transcription

## Decision: WhisperX Model Selection
- Chosen: Use WhisperX with "large-v3" model for optimal accuracy
- Rationale: Large-v3 provides best transcription quality for multi-speaker audio
- Alternatives considered: Smaller models (faster but less accurate), OpenAI Whisper API (cloud dependency)

## Decision: GPU Acceleration
- Chosen: CUDA acceleration when available, CPU fallback
- Rationale: GPU significantly speeds up transcription while maintaining CPU compatibility
- Alternatives considered: CPU-only (slower), cloud GPU services (additional complexity)

## Decision: Speaker Diarization
- Chosen: pyannote.audio for speaker diarization when enabled
- Rationale: Industry-standard diarization with good accuracy for Discord voice channels
- Alternatives considered: Built-in WhisperX diarization, manual speaker assignment

## Decision: Output Schema
- Chosen: JSON schema with segments array, each containing start/end times, text, speaker, words array
- Rationale: Structured, queryable format compatible with downstream processing
- Alternatives considered: SRT subtitles, plain text with timestamps

## Decision: Asynchronous Processing
- Chosen: asyncio with ThreadPoolExecutor for WhisperX operations
- Rationale: Keeps bot responsive while handling long-running transcription tasks
- Alternatives considered: Synchronous processing (blocks bot), separate worker processes
