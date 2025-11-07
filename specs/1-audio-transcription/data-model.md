# Data Model: audio-transcription

## Entities

### TranscriptSegment
- start_time: float (seconds)
- end_time: float (seconds)
- text: string
- speaker_label: string (optional, null if diarization disabled)
- words: array of objects with {word: string, start: float, end: float, confidence: float}

### TranscriptionLog
- timestamp: ISO datetime string
- runtime: float (seconds)
- model_name: string ("large-v3")
- accuracy_metrics: object with confidence scores
- errors: array of error messages (empty if successful)

## Relationships
- Transcript contains multiple TranscriptSegments
- Each transcription has one TranscriptionLog

## Validation Rules
- start_time < end_time for all segments
- speaker_label consistent across segments for same speaker
- words array timestamps align with segment boundaries
- accuracy_metrics include word-level confidence scores
