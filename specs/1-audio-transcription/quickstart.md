# Quickstart: audio-transcription

## Prerequisites
- Python 3.7+
- WhisperX installed (`pip install whisperx`)
- GPU with CUDA support (optional, CPU fallback available)
- Audio file in 16kHz mono WAV format
- Session metadata JSON

## Steps
1. Ensure WhisperX dependencies are installed
2. Prepare audio file (session_audio_16k.wav) and metadata (metadata.json)
3. Run transcription service with optional diarization
4. Check output transcript.json and transcription log
5. Validate timestamps and speaker labels if diarization enabled

## Validation
- Verify transcript.json schema compliance
- Check timestamp accuracy against audio playback
- Review transcription log for runtime and accuracy metrics
- Run pytest for automated validation
- Manual review of diarization results
