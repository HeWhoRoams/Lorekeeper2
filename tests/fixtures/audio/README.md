# Test Audio Fixtures

This directory contains test audio files for validating bot functionality.

## Files

### single_speaker_10s.wav
- **Duration**: 10 seconds
- **Sample Rate**: 16000 Hz
- **Channels**: 1 (mono)
- **Content**: Single speaker saying "Hello, this is a test transcription. The quick brown fox jumps over the lazy dog."
- **Purpose**: Basic transcription accuracy test

### multi_speaker_30s.wav
- **Duration**: 30 seconds
- **Sample Rate**: 16000 Hz
- **Channels**: 1 (mono)
- **Content**: Two speakers having a conversation
- **Purpose**: Speaker diarization test

### corrupted.wav
- **Content**: Intentionally corrupted audio file
- **Purpose**: Error handling test

## Creating Test Audio

To create new test audio files:

1. Record audio at 16000 Hz, mono, 16-bit PCM WAV format
2. Use clear speech with minimal background noise
3. Keep duration reasonable (<60s for most tests)
4. Document content and expected transcript

### Example using ffmpeg:
```bash
ffmpeg -i input.wav -ar 16000 -ac 1 -sample_fmt s16 output_16k.wav
```

## Note

Actual audio files are not committed to git due to size. Run the test fixture generator script to create sample audio programmatically, or record real audio for more realistic testing.
