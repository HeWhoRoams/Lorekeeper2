# Data Model: Transcription Testing Suite

## Entities

### TestAudioSession
- session_id: string (unique identifier)
- audio_file_path: string (path to test audio WAV file)
- metadata_file_path: string (path to test metadata JSON)
- expected_duration: float (seconds)
- expected_sample_rate: int (Hz, typically 16000)
- expected_users: array of user_id strings
- description: string (what this test case covers)

### TranscriptTestCase
- test_id: string (unique identifier)
- audio_session: TestAudioSession reference
- expected_transcript_path: string (path to expected transcript JSON)
- enable_diarization: boolean
- min_speakers: int (optional)
- max_speakers: int (optional)
- expected_segment_count: int (approximate)
- expected_accuracy: float (0.0-1.0, word error rate tolerance)

### TestResultLog
- test_run_id: string (unique identifier for test run)
- timestamp: ISO datetime string
- test_case: TranscriptTestCase reference
- status: string (PASS, FAIL, SKIP, ERROR)
- actual_output_path: string (path to generated transcript)
- errors: array of error messages
- metrics: object with accuracy, duration, segment_count, etc.
- manual_review_status: string (PENDING, PASS, FAIL, N/A)

## Relationships
- TestAudioSession contains audio and metadata for one or more TranscriptTestCases
- TranscriptTestCase references one TestAudioSession and one expected output
- TestResultLog references one TranscriptTestCase and captures actual results

## Validation Rules
- audio_file_path must exist and be valid WAV format
- expected_duration > 0
- expected_sample_rate must be 8000, 16000, or 48000
- expected_accuracy between 0.0 and 1.0
- status must be one of: PASS, FAIL, SKIP, ERROR
- manual_review_status must be one of: PENDING, PASS, FAIL, N/A
