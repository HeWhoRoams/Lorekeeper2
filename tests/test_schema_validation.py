"""
Tests for schema validation of transcription outputs.
"""
import pytest
from src.testing.validators import (
    validate_transcript_schema,
    validate_metadata_schema,
    validate_log_entry
)


class TestTranscriptSchemaValidation:
    """Test transcript JSON schema validation."""
    
    def test_valid_transcript_passes(self, single_speaker_expected):
        """Test that a valid transcript passes schema validation."""
        errors = validate_transcript_schema(single_speaker_expected)
        assert errors == [], f"Valid transcript should have no errors: {errors}"
    
    def test_missing_metadata_fails(self, single_speaker_expected):
        """Test that missing metadata field is detected."""
        invalid = single_speaker_expected.copy()
        del invalid["metadata"]
        errors = validate_transcript_schema(invalid)
        assert any("metadata" in e for e in errors)
    
    def test_missing_segments_fails(self, single_speaker_expected):
        """Test that missing segments field is detected."""
        invalid = single_speaker_expected.copy()
        del invalid["segments"]
        errors = validate_transcript_schema(invalid)
        assert any("segments" in e for e in errors)
    
    def test_missing_log_fails(self, single_speaker_expected):
        """Test that missing log field is detected."""
        invalid = single_speaker_expected.copy()
        del invalid["log"]
        errors = validate_transcript_schema(invalid)
        assert any("log" in e for e in errors)
    
    def test_invalid_segment_timestamps_fails(self, single_speaker_expected):
        """Test that invalid segment timestamps are detected."""
        invalid = single_speaker_expected.copy()
        invalid["segments"][0]["end_time"] = invalid["segments"][0]["start_time"] - 1
        errors = validate_transcript_schema(invalid)
        assert any("end_time must be > start_time" in e for e in errors)
    
    def test_missing_segment_fields_fails(self, single_speaker_expected):
        """Test that missing segment fields are detected."""
        invalid = single_speaker_expected.copy()
        del invalid["segments"][0]["text"]
        errors = validate_transcript_schema(invalid)
        assert any("missing field: text" in e for e in errors)


class TestMetadataSchemaValidation:
    """Test session metadata schema validation."""
    
    def test_valid_metadata_passes(self, valid_metadata):
        """Test that valid metadata passes schema validation."""
        errors = validate_metadata_schema(valid_metadata)
        assert errors == [], f"Valid metadata should have no errors: {errors}"
    
    def test_missing_guild_id_fails(self, valid_metadata):
        """Test that missing guild_id is detected."""
        invalid = valid_metadata.copy()
        del invalid["guild_id"]
        errors = validate_metadata_schema(invalid)
        assert any("guild_id" in e for e in errors)
    
    def test_missing_users_fails(self, valid_metadata):
        """Test that missing users field is detected."""
        invalid = valid_metadata.copy()
        del invalid["users"]
        errors = validate_metadata_schema(invalid)
        assert any("users" in e for e in errors)
    
    def test_invalid_timestamps_fails(self, valid_metadata):
        """Test that invalid timestamps are detected."""
        invalid = valid_metadata.copy()
        invalid["end_time"] = invalid["start_time"] - 1
        errors = validate_metadata_schema(invalid)
        assert any("end_time must be > start_time" in e for e in errors)
    
    def test_invalid_sample_rate_fails(self, valid_metadata):
        """Test that invalid sample rate is detected."""
        invalid = valid_metadata.copy()
        invalid["sample_rate"] = -1
        errors = validate_metadata_schema(invalid)
        assert any("sample_rate" in e for e in errors)


class TestLogEntryValidation:
    """Test transcription log entry schema validation."""
    
    def test_valid_log_entry_passes(self):
        """Test that a valid log entry passes validation."""
        log_entry = {
            "date": "2024-01-15",
            "begin": 1705334400.0,
            "end": 1705334410.0,
            "user_id": "123456789",
            "player": "Alice",
            "character": "Elara",
            "event_source": "transcription",
            "data": {"text": "Hello world"}
        }
        errors = validate_log_entry(log_entry)
        assert errors == []
    
    def test_missing_required_fields_fails(self):
        """Test that missing required fields are detected."""
        incomplete = {
            "date": "2024-01-15",
            "begin": 1705334400.0
        }
        errors = validate_log_entry(incomplete)
        assert len(errors) > 0
        assert any("end" in e for e in errors)
    
    def test_invalid_timestamps_fails(self):
        """Test that invalid timestamps are detected."""
        invalid = {
            "date": "2024-01-15",
            "begin": 1705334410.0,
            "end": 1705334400.0,
            "user_id": "123456789",
            "player": "Alice",
            "character": "Elara",
            "event_source": "transcription",
            "data": {"text": "Hello"}
        }
        errors = validate_log_entry(invalid)
        assert any("timestamp" in e.lower() for e in errors)
    
    def test_missing_data_text_fails(self):
        """Test that missing text in data is detected."""
        invalid = {
            "date": "2024-01-15",
            "begin": 1705334400.0,
            "end": 1705334410.0,
            "user_id": "123456789",
            "player": "Alice",
            "character": "Elara",
            "event_source": "transcription",
            "data": {}
        }
        errors = validate_log_entry(invalid)
        assert any("text" in e for e in errors)
