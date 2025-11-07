# Transcription Bot Testing Suite

Comprehensive testing infrastructure for the V.O.L.O Discord transcription bot.

## Test Structure

```
tests/
├── conftest.py                    # pytest configuration and shared fixtures
├── test_schema_validation.py     # Schema validation tests (fully automated)
├── test_audio_saving.py          # Audio file format tests (mostly automated)
├── test_transcription.py         # Transcription accuracy tests (integration)
├── test_bot_commands.py          # Discord command tests (manual)
└── fixtures/
    ├── audio/                     # Test audio files
    │   ├── README.md
    │   ├── generate_audio.py      # Script to generate test audio
    │   ├── single_speaker_10s.wav
    │   ├── multi_speaker_30s.wav
    │   ├── corrupted.wav
    │   └── silent_5s.wav
    ├── metadata/                  # Session metadata fixtures
    │   └── valid_metadata.json
    └── expected_outputs/          # Expected transcription results
        └── single_speaker_transcript.json
```

## Running Tests

### Quick Start
```bash
# Run all automated tests
pytest tests/

# Run specific test file
pytest tests/test_schema_validation.py

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html
```

### Test Categories

**Automated Tests** (can run in CI):
- `test_schema_validation.py` - All tests runnable without models
- `test_audio_saving.py` - Audio format validation (requires fixtures)

**Integration Tests** (require Whisper models):
- `test_transcription.py` - Most tests marked with `@pytest.mark.skip`
- Run with: `pytest tests/test_transcription.py -v -m "not skip"`

**Manual Tests** (require Discord bot running):
- `test_bot_commands.py` - All tests require live Discord connection
- Follow test docstrings for manual testing procedures

### Generate Test Audio Fixtures
```bash
# Generate synthetic test audio files
cd tests/fixtures
python generate_audio.py

# Note: For realistic multi-speaker testing, manually record audio
```

## Test Validation Criteria

### Schema Validation Tests
- ✅ Valid transcripts pass validation (0 errors)
- ✅ Missing required fields detected
- ✅ Invalid timestamps caught
- ✅ Malformed data structures rejected

### Audio Saving Tests
- ✅ Audio files are mono (1 channel)
- ✅ Audio files are 16-bit PCM
- ✅ Audio files have 16kHz sample rate
- ✅ Corrupted files detected

### Transcription Tests
- ✅ Single speaker transcription accuracy > 90%
- ✅ Multi-speaker detection (diarization)
- ✅ Word Error Rate (WER) < 10% for clear audio
- ✅ Graceful error handling for edge cases

### Bot Command Tests
- ✅ All commands respond appropriately
- ✅ Voice channel connection/disconnection works
- ✅ Recording captures audio correctly
- ✅ Async transcription jobs complete successfully

## Manual Testing Procedures

### 1. Voice Channel Commands
```
1. Join a voice channel in Discord
2. Run /connect → Verify bot joins
3. Run /disconnect → Verify bot leaves
```

### 2. Recording Session
```
1. /connect to voice channel
2. /start_recording
3. Speak for 10-15 seconds
4. /stop_recording
5. Verify .logs/audio/ contains WAV + metadata JSON
```

### 3. Synchronous Transcription
```
1. /transcribe_now <audio_file_path>
2. Wait for completion (command blocks)
3. Verify .logs/transcripts/ contains JSON
4. Verify results posted to Discord
```

### 4. Asynchronous Transcription
```
1. /transcribe_async <audio_file_path>
2. Note returned job_id
3. /transcription_status <job_id> → Check progress
4. /notify_on_completion <job_id>
5. Verify notification when complete
```

## Troubleshooting

### Tests Fail with Import Errors
```bash
# Ensure all dependencies installed
pip install -r requirements.txt

# Verify Python path includes src/
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Audio Fixture Tests Skipped
```bash
# Generate audio fixtures
cd tests/fixtures
python generate_audio.py
```

### Integration Tests Fail
```bash
# Ensure Whisper model downloaded
python -c "from src.transcription.model_manager import ModelManager; ModelManager('base')"

# Check GPU availability
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

### Bot Command Tests Can't Run
Manual tests require:
1. Discord bot running (`python main.py`)
2. Valid `DISCORD_BOT_TOKEN` in `.env`
3. Bot invited to test server
4. User in voice channel

## Adding New Tests

### 1. Create Test File
```python
# tests/test_new_feature.py
import pytest

class TestNewFeature:
    def test_something(self):
        assert True
```

### 2. Add Fixtures (if needed)
```python
# tests/conftest.py
@pytest.fixture
def new_fixture():
    return {"key": "value"}
```

### 3. Run Tests
```bash
pytest tests/test_new_feature.py -v
```

## Continuous Integration

For CI/CD pipelines, run only automated tests:
```bash
# Run non-integration tests
pytest tests/test_schema_validation.py -v

# Or exclude integration tests
pytest tests/ -v -m "not skip"
```

## References

- [pytest documentation](https://docs.pytest.org/)
- [Whisper model details](https://github.com/openai/whisper)
- [Discord.py testing guide](https://discordpy.readthedocs.io/en/stable/faq.html#how-do-i-test-my-bot)
