# Data Model: audio_capture

## Entities

### SessionAudio
- file_path: string
- format: string ("WAV")
- sample_rate: integer (16000)
- channels: integer (1)
- bit_depth: integer (16)
- duration: float (seconds)

### SessionMetadata
- guild_id: string
- channel_id: string
- participants: list of strings (user IDs)
- start_time: ISO datetime string
- end_time: ISO datetime string
- duration: float (seconds)
- file_path: string

## Relationships
- Each SessionAudio is linked to one SessionMetadata
- SessionMetadata references the corresponding SessionAudio file

## Validation Rules
- Audio file MUST be mono, 16kHz, 16-bit PCM
- Metadata MUST list all required fields and match session details
- Duration in metadata MUST match audio file duration
