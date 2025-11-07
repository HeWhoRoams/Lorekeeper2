# Quickstart: Transcription Testing Suite

## Prerequisites
- Python 3.7+
- All bot dependencies installed (`pip install -r requirements.txt`)
- pytest installed (`pip install pytest pytest-asyncio`)
- Test audio fixtures in `tests/fixtures/audio/`
- Expected output fixtures in `tests/fixtures/expected_outputs/`

## Running Automated Tests

### 1. Run All Tests
```bash
pytest tests/ -v
```

### 2. Run Specific Test Categories
```bash
# Audio saving tests only
pytest tests/test_audio_saving.py -v

# Transcription accuracy tests only
pytest tests/test_transcription.py -v

# Schema validation tests only
pytest tests/test_schema_validation.py -v

# Bot command tests only
pytest tests/test_bot_commands.py -v
```

### 3. Run with Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

### 4. Run in CI/CD
```bash
pytest tests/ --junitxml=test-results.xml
```

## Manual Review Process

### Step 1: Listen to Test Audio
1. Open `tests/fixtures/audio/single_speaker_10s.wav` in audio player
2. Note speaker count, words spoken, approximate timestamps
3. Compare with expected transcript in `tests/fixtures/expected_outputs/single_speaker_transcript.json`

### Step 2: Verify Transcript Quality
- [ ] Text matches actual spoken words (>95% accuracy)
- [ ] Timestamps align within ±250ms of actual audio
- [ ] Speaker labels (if diarization enabled) are consistent and correct
- [ ] JSON schema is valid and complete

### Step 3: Check Logs
- [ ] Transcription log includes runtime, model name, accuracy metrics
- [ ] No unexpected errors or warnings
- [ ] Log format matches structured JSON schema

### Step 4: Edge Case Validation
- [ ] Corrupted audio files handled gracefully with error messages
- [ ] Malformed metadata files handled gracefully
- [ ] Very short (<1s) and very long (>2hr) audio handled correctly

## Validation Criteria

### Automated Tests
- All pytest tests pass (100% pass rate for valid fixtures)
- Schema validation confirms all outputs match expected format
- Accuracy metrics within acceptable thresholds (>95% for known audio)

### Manual Review
- Human review confirms transcripts match audio playback
- Speaker labels are intuitive and consistent
- Logs provide actionable debugging information

## Creating New Test Cases

1. Add new test audio to `tests/fixtures/audio/your_test.wav`
2. Create metadata file `tests/fixtures/metadata/your_test_metadata.json`
3. Generate expected output by running transcription manually
4. Save expected output to `tests/fixtures/expected_outputs/your_test_transcript.json`
5. Add test case to appropriate test file (e.g., `tests/test_transcription.py`)
6. Run tests to verify new case passes

## Troubleshooting

- **Tests fail with "fixture not found"**: Ensure test audio files exist in `tests/fixtures/audio/`
- **Accuracy below threshold**: Check if test audio quality is poor or expected output needs updating
- **Schema validation fails**: Compare actual output with expected schema in `src/transcription/validator.py`
- **Diarization tests fail**: Ensure HF_TOKEN is set in .env and pyannote.audio is installed
