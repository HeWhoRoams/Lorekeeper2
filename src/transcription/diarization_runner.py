"""
Diarization runner that integrates speaker diarization with WhisperX transcription.

Combines WhisperX transcription and alignment with pyannote speaker diarization
to provide complete multi-speaker transcription with speaker labels.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .diarization_service import DiarizationService
from .whisper_runner import WhisperRunner
from ..models.transcript_segment import TranscriptSegment
from ..models.transcription_log import TranscriptionLog


class DiarizationRunner:
    """
    Integrated transcription and diarization runner.

    Combines WhisperX transcription with speaker diarization to provide
    complete multi-speaker audio transcription with speaker attribution.
    """

    def __init__(self, model_name: str = "large-v3", auth_token: Optional[str] = None):
        """
        Initialize the diarization runner.

        Args:
            model_name: WhisperX model to use
            auth_token: HuggingFace authentication token for pyannote
        """
        self.model_name = model_name
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize components
        self.whisper_runner = WhisperRunner(model_name)
        self.diarization_service = DiarizationService(auth_token)

    def transcribe_with_diarization(self, audio_path: Path,
                                  language: str = "en") -> Tuple[List[TranscriptSegment], TranscriptionLog]:
        """
        Transcribe audio with speaker diarization.

        Args:
            audio_path: Path to the audio file
            language: Language code for transcription

        Returns:
            Tuple of (transcript_segments_with_speakers, transcription_log)
        """
        start_time = datetime.now()

        try:
            self.logger.info(f"Starting transcription with diarization: {audio_path}")

            # Step 1: Run WhisperX transcription and alignment
            self.logger.info("Running WhisperX transcription...")
            segments, whisper_log = self.whisper_runner.transcribe_audio(audio_path, language)

            # Step 2: Run speaker diarization
            self.logger.info("Running speaker diarization...")
            diarization_result = self.diarization_service.diarize_audio(audio_path)

            # Step 3: Combine results
            if diarization_result and self.diarization_service.validate_diarization_result(diarization_result):
                self.logger.info("Assigning speakers to transcript segments...")
                segments_with_speakers = self.diarization_service.assign_speakers_to_segments(
                    segments, diarization_result
                )

                # Add diarization metrics to log
                speaker_summary = self.diarization_service.get_speaker_summary(diarization_result)
                if speaker_summary:
                    whisper_log.accuracy_metrics.update({
                        "diarization_speakers_detected": speaker_summary["total_speakers"],
                        "diarization_total_duration": speaker_summary["total_duration"]
                    })

                self.logger.info(f"Diarization successful: {speaker_summary['total_speakers']} speakers detected")
            else:
                self.logger.warning("Diarization failed or returned invalid results, proceeding without speaker labels")
                segments_with_speakers = segments
                whisper_log.errors.append("Speaker diarization failed")

            # Update runtime to include diarization time
            whisper_log.runtime = (datetime.now() - start_time).total_seconds()

            self.logger.info(f"Transcription with diarization completed in {whisper_log.runtime:.2f}s")
            return segments_with_speakers, whisper_log

        except Exception as e:
            error_msg = f"Transcription with diarization failed: {e}"
            self.logger.error(error_msg)

            # Create error log
            error_log = TranscriptionLog.create_log(
                model_name=self.model_name,
                start_time=start_time,
                accuracy_metrics={},
                errors=[str(e)]
            )

            raise RuntimeError(error_msg) from e

    def get_diarization_status(self) -> Dict[str, Any]:
        """
        Get the status of diarization capabilities.

        Returns:
            Dictionary with diarization status information
        """
        status = {
            "diarization_available": self.diarization_service.pipeline is not None,
            "whisper_available": True,  # Assume available if we got this far
        }

        if self.diarization_service.pipeline:
            status["auth_token_configured"] = self.diarization_service.auth_token is not None
        else:
            status["error"] = "pyannote.audio not available or initialization failed"

        return status

    def validate_multi_speaker_audio(self, audio_path: Path) -> Dict[str, Any]:
        """
        Validate if audio contains multiple speakers and estimate diarization quality.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with validation results
        """
        validation = {
            "audio_path": str(audio_path),
            "multi_speaker_likely": False,
            "estimated_speakers": 1,
            "diarization_recommended": False
        }

        try:
            # Get audio info
            audio_info = self.whisper_runner.audio_loader.get_audio_info(audio_path)
            if audio_info:
                duration = audio_info.get("duration_seconds", 0)

                # Simple heuristics for multi-speaker detection
                # (This is a basic implementation - could be enhanced with voice activity detection)
                if duration > 300:  # Longer than 5 minutes
                    validation["multi_speaker_likely"] = True
                    validation["estimated_speakers"] = min(5, max(2, int(duration / 180)))  # Rough estimate
                    validation["diarization_recommended"] = True

                validation["duration_seconds"] = duration

        except Exception as e:
            self.logger.warning(f"Could not validate audio for multi-speaker detection: {e}")
            validation["error"] = str(e)

        return validation