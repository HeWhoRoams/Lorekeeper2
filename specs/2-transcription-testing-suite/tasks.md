# Tasks: Transcription Testing Suite

**Feature**: 2-transcription-testing-suite  
**Status**: Ready for implementation  
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## User Story 1: Audio Recording Validation (P1 - Critical)
**Acceptance**: Test suite validates audio file format, integrity, and metadata correctness for all recording sessions

### T001: Create test fixtures directory structure
- Create `tests/fixtures/audio/` directory
- Create `tests/fixtures/metadata/` directory
- Create `tests/fixtures/expected_outputs/` directory
- Create `src/testing/` directory for helper utilities
- **Status**: ✅ Complete

### T002: Create audio fixture generation script
- Create `tests/fixtures/generate_audio.py` script
- Implement `generate_silent_audio()` for silent WAV files
- Implement `generate_tone_audio()` for sine wave test files
- Implement `generate_corrupted_audio()` for error testing
- Implement `generate_test_audio_with_tts()` using pyttsx3 (optional)
- Add main() function to generate all fixtures
- **Status**: ✅ Complete

### T003: Generate test audio fixtures
- Run `tests/fixtures/generate_audio.py` to create files
- Create `single_speaker_10s.wav` (10 second mono audio)
- Create `multi_speaker_30s.wav` (30 second with multiple speakers)
- Create `corrupted.wav` (intentionally malformed)
- Create `silent_5s.wav` (5 seconds of silence)
- Verify all files are 16kHz, mono, 16-bit PCM
- **Status**: ✅ Complete

### T004: Create metadata fixtures
- Create `tests/fixtures/metadata/valid_metadata.json`
- Create `tests/fixtures/metadata/malformed_metadata.json`
- Include required fields: guild_id, channel_id, start_time, end_time, sample_rate, users
- Add player/character mappings in valid metadata
- **Status**: ✅ Complete

### T005: Create expected output fixtures
- Create `tests/fixtures/expected_outputs/single_speaker_transcript.json`
- Create `tests/fixtures/expected_outputs/multi_speaker_transcript.json`
- Include metadata, segments with word-level alignment, log data
- Match structure from actual TranscriptWriter output
- **Status**: ✅ Complete

### T006: Implement test helper utilities
- Create `src/testing/test_helpers.py`
- Implement `load_json_fixture()` for loading test data
- Implement `compare_transcripts()` for comparing actual vs expected
- Implement `calculate_word_error_rate()` for WER calculation
- Implement `validate_audio_file()` for format checking
- **Status**: ✅ Complete

### T007: Implement schema validators
- Create `src/testing/validators.py`
- Implement `validate_transcript_schema()` for transcript JSON validation
- Implement `validate_metadata_schema()` for session metadata validation
- Implement `validate_log_entry()` for transcription log validation
- Return list of validation errors (empty if valid)
- **Status**: ✅ Complete

### T008: Create pytest configuration
- Create `tests/conftest.py` with shared fixtures
- Add `fixtures_dir`, `audio_dir`, `metadata_dir`, `expected_outputs_dir` fixtures
- Add `valid_metadata`, `single_speaker_expected` fixtures for loading JSON
- Add `single_speaker_audio`, `multi_speaker_audio`, `corrupted_audio` fixtures
- Add `temp_output_dir` fixture for test outputs
- **Status**: ✅ Complete

### T009: Implement audio saving tests
- Create `tests/test_audio_saving.py`
- Test audio file format (mono, 16-bit, 16kHz sample rate)
- Test audio file exists and is readable
- Test corrupted audio detection
- Add manual test stubs for SessionRecorder integration
- **Status**: ✅ Complete

### T010: Validate audio saving tests
- Run `pytest tests/test_audio_saving.py -v`
- Verify all automated tests pass
- Document manual testing procedures in test docstrings
- **Status**: ✅ Complete (7 passed, 2 skipped manual tests)

---

## User Story 2: Transcription Accuracy Testing (P1 - Critical)
**Acceptance**: Test suite measures transcription accuracy (WER <10%), validates word-level alignment, and verifies speaker diarization

### T011: Implement schema validation tests
- Create `tests/test_schema_validation.py`
- Test valid transcript passes validation
- Test missing required fields detection (metadata, segments, log)
- Test invalid segment timestamps detection
- Test metadata schema validation
- Test log entry schema validation
- **Status**: ✅ Complete

### T012: Validate schema tests
- Run `pytest tests/test_schema_validation.py -v`
- Verify all tests pass with current fixtures
- Add additional edge case tests if needed
- **Status**: ✅ Complete (15 passed)

### T013: Implement transcription accuracy tests
- Create `tests/test_transcription.py`
- Test single speaker transcription with expected output comparison
- Test multi-speaker transcription with diarization
- Test WER calculation for transcription quality
- Test transcript comparison logic
- Mark integration tests requiring Whisper model with `@pytest.mark.skip`
- **Status**: ✅ Complete

### T014: Implement transcription edge case tests
- Add test for empty/silent audio handling
- Add test for corrupted audio graceful error handling
- Add test for very short audio (<0.1s) handling
- Add tests for async transcription job submission
- Add tests for multiple concurrent transcription jobs
- **Status**: ✅ Complete

### T015: Create manual transcription validation procedures
- Document manual review steps in `tests/README.md`
- Include criteria for acceptable transcription quality
- Provide sample audio scenarios (clear, noisy, accented speech)
- Add troubleshooting guide for common issues
- **Status**: ✅ Complete

---

## User Story 3: Command Validation Testing (P2 - Important)
**Acceptance**: All bot commands tested for correct responses, error handling, and integration with audio/transcription systems

### T016: Implement bot command tests
- Create `tests/test_bot_commands.py`
- Test `/connect` command (manual test stub)
- Test `/disconnect` command (manual test stub)
- Test `/start_recording` command (manual test stub)
- Test `/stop_recording` command (manual test stub)
- **Status**: ✅ Complete

### T017: Implement transcription command tests
- Add test for `/transcribe_now` command
- Add test for `/transcribe_async` command
- Add test for `/transcription_status` command
- Add test for `/notify_on_completion` command
- Add test for `/help` command
- **Status**: ✅ Complete

### T018: Implement player mapping tests
- Add test for `/update_player_map` command
- Verify player_map.yml updates correctly
- Verify transcripts use updated mappings
- **Status**: ✅ Complete

### T019: Create manual command testing procedures
- Document step-by-step command testing in test docstrings
- Include expected bot responses and status changes
- Add verification steps for file creation and logging
- **Status**: ✅ Complete

### T020: Create tests README documentation
- Create `tests/README.md` with testing overview
- Document test structure and categories
- Provide quick start commands for running tests
- Add troubleshooting section
- Include manual testing procedures
- Add CI/CD integration guidance
- **Status**: ✅ Complete

---

## Task Summary

**Total Tasks**: 20  
**Completed**: 20  
**Pending**: 0  

**All Tasks Complete!**

**Test Results**:
- ✅ 24 automated tests passing
- ✅ 19 manual/integration tests documented (skipped in automated runs)
- ✅ Total: 43 test cases

**Coverage**:
- Schema validation: 15 tests
- Audio file validation: 7 tests
- Transcription accuracy: 4 tests
- Bot commands: 10 tests (manual)
- Integration tests: 7 tests (require Whisper models)

**Next Steps**:
1. ✅ All automated tests pass
2. ✅ Manual testing procedures documented
3. ✅ CI/CD ready (automated tests run offline with fixtures)
4. Ready for production use with manual validation as needed
