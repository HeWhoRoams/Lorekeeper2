"""
Tests for audio saving and file format validation.
"""
import pytest
import wave
from pathlib import Path
from src.testing.test_helpers import validate_audio_file


class TestAudioFileFormat:
    """Test audio file format and properties."""
    
    def test_single_speaker_audio_format(self, single_speaker_audio):
        """Test that single speaker audio has correct format."""
        errors = validate_audio_file(
            str(single_speaker_audio),
            expected_sample_rate=16000,
            expected_duration=10.0
        )
        assert errors == [], f"Audio format validation failed: {errors}"
    
    def test_multi_speaker_audio_format(self, multi_speaker_audio):
        """Test that multi-speaker audio has correct format."""
        errors = validate_audio_file(
            str(multi_speaker_audio),
            expected_sample_rate=16000,
            expected_duration=30.0
        )
        assert errors == [], f"Audio format validation failed: {errors}"
    
    def test_audio_is_mono(self, single_speaker_audio):
        """Test that audio is single-channel (mono)."""
        with wave.open(str(single_speaker_audio), 'rb') as wav:
            channels = wav.getnchannels()
            assert channels == 1, f"Expected mono audio, got {channels} channels"
    
    def test_audio_is_16bit(self, single_speaker_audio):
        """Test that audio is 16-bit."""
        with wave.open(str(single_speaker_audio), 'rb') as wav:
            sample_width = wav.getsampwidth()
            assert sample_width == 2, f"Expected 16-bit audio, got {sample_width * 8}-bit"
    
    def test_audio_sample_rate(self, single_speaker_audio):
        """Test that audio has correct sample rate."""
        with wave.open(str(single_speaker_audio), 'rb') as wav:
            sample_rate = wav.getframerate()
            assert sample_rate == 16000, f"Expected 16kHz sample rate, got {sample_rate}Hz"


class TestAudioSaving:
    """Test audio file saving and metadata."""
    
    def test_audio_file_exists(self, single_speaker_audio):
        """Test that audio file exists and is readable."""
        assert single_speaker_audio.exists()
        assert single_speaker_audio.is_file()
        assert single_speaker_audio.stat().st_size > 0
    
    def test_corrupted_audio_detection(self, corrupted_audio):
        """Test that corrupted audio is detected."""
        # This test expects the audio validation to catch corruption
        errors = validate_audio_file(str(corrupted_audio), expected_sample_rate=16000)
        # Corrupted files should fail validation
        assert len(errors) > 0, "Corrupted audio should be detected"


class TestSessionRecording:
    """Test SessionRecorder audio capture functionality."""
    
    @pytest.mark.skip(reason="Requires Discord voice connection - manual testing only")
    def test_session_recorder_creates_files(self):
        """
        Manual test: Verify SessionRecorder creates audio files during recording.
        
        Steps:
        1. Start bot and connect to voice channel
        2. Run /start_recording
        3. Speak for 10 seconds
        4. Run /stop_recording
        5. Verify .logs/audio/ contains WAV file
        """
        pass
    
    @pytest.mark.skip(reason="Requires Discord voice connection - manual testing only")
    def test_session_recorder_saves_metadata(self):
        """
        Manual test: Verify SessionRecorder saves metadata JSON.
        
        Steps:
        1. Complete recording session
        2. Verify .logs/audio/ contains metadata JSON
        3. Verify metadata includes guild_id, users, timestamps
        """
        pass
