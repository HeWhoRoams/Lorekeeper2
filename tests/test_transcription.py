"""
Tests for audio transcription functionality.
"""
import pytest
import json
from pathlib import Path
from src.testing.test_helpers import compare_transcripts, calculate_word_error_rate
from src.transcription.transcription_service import TranscriptionService
from src.transcription.model_manager import ModelManager


class TestTranscriptionAccuracy:
    """Test transcription accuracy and quality."""
    
    @pytest.mark.skip(reason="Requires Whisper model - integration test only")
    def test_single_speaker_transcription(self, single_speaker_audio, single_speaker_expected, temp_output_dir):
        """
        Integration test: Transcribe single speaker audio and compare with expected output.
        
        This test requires Whisper model to be available.
        """
        # Initialize transcription service
        service = TranscriptionService(
            model_manager=ModelManager(model_name="base"),
            output_dir=str(temp_output_dir)
        )
        
        # Transcribe audio
        result = service.transcribe_audio(str(single_speaker_audio))
        
        # Compare with expected output
        differences = compare_transcripts(result, single_speaker_expected, tolerance_ms=500)
        assert len(differences) == 0, f"Transcription differences: {differences}"
    
    @pytest.mark.skip(reason="Requires Whisper model - integration test only")
    def test_multi_speaker_transcription(self, multi_speaker_audio, temp_output_dir):
        """
        Integration test: Transcribe multi-speaker audio and verify speaker labels.
        """
        service = TranscriptionService(
            model_manager=ModelManager(model_name="base"),
            output_dir=str(temp_output_dir),
            enable_diarization=True
        )
        
        result = service.transcribe_audio(str(multi_speaker_audio))
        
        # Verify multiple speakers detected
        speakers = set(seg["speaker"] for seg in result["segments"])
        assert len(speakers) > 1, f"Expected multiple speakers, got {len(speakers)}"
    
    def test_word_error_rate_calculation(self):
        """Test WER calculation between actual and expected text."""
        expected = "Hello world this is a test"
        actual = "Hello world this is a test"
        wer = calculate_word_error_rate(actual, expected)
        assert wer == 0.0, "Identical text should have WER of 0"
        
        actual_with_errors = "Hello world this was a fest"
        wer = calculate_word_error_rate(actual_with_errors, expected)
        assert 0 < wer < 1, f"Expected WER between 0 and 1, got {wer}"
    
    def test_transcript_comparison(self, single_speaker_expected):
        """Test transcript comparison logic."""
        # Identical transcripts should have no differences
        differences = compare_transcripts(single_speaker_expected, single_speaker_expected)
        assert len(differences) == 0
        
        # Different segment counts should be detected
        modified = single_speaker_expected.copy()
        modified["segments"] = modified["segments"][:1]
        differences = compare_transcripts(modified, single_speaker_expected)
        assert len(differences) > 0
        assert any("Segment count mismatch" in d for d in differences)


class TestTranscriptionEdgeCases:
    """Test transcription edge cases and error handling."""
    
    @pytest.mark.skip(reason="Requires Whisper model - integration test only")
    def test_empty_audio_handling(self, temp_output_dir):
        """Test handling of silent/empty audio."""
        # This would require generating a silent audio file
        pass
    
    @pytest.mark.skip(reason="Requires Whisper model - integration test only")
    def test_corrupted_audio_handling(self, corrupted_audio, temp_output_dir):
        """Test graceful handling of corrupted audio files."""
        service = TranscriptionService(
            model_manager=ModelManager(model_name="base"),
            output_dir=str(temp_output_dir)
        )
        
        # Should handle error gracefully, not crash
        with pytest.raises(Exception) as exc_info:
            service.transcribe_audio(str(corrupted_audio))
        
        # Verify error message is informative
        assert "audio" in str(exc_info.value).lower() or "file" in str(exc_info.value).lower()
    
    @pytest.mark.skip(reason="Requires Whisper model - integration test only")
    def test_very_short_audio_handling(self, temp_output_dir):
        """Test handling of very short audio (< 0.1s)."""
        # Whisper requires minimum 0.1s audio
        # This would require generating a very short audio file
        pass


class TestAsyncTranscription:
    """Test asynchronous transcription processing."""
    
    @pytest.mark.skip(reason="Requires Discord bot context - integration test only")
    def test_async_job_submission(self):
        """
        Integration test: Submit async transcription job and verify it completes.
        
        Steps:
        1. Submit job via TranscriptionJobManager
        2. Verify job_id is returned
        3. Poll job status until complete
        4. Verify output files exist
        """
        pass
    
    @pytest.mark.skip(reason="Requires Discord bot context - integration test only")
    def test_multiple_concurrent_jobs(self):
        """
        Integration test: Submit multiple transcription jobs concurrently.
        
        Verify:
        - All jobs complete successfully
        - No race conditions or resource conflicts
        - Each job produces correct output
        """
        pass
