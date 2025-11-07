"""
Base transcription service for audio processing.

Provides the core interface and common functionality for audio transcription
services, including WhisperX integration and result formatting.
"""

import json
import logging
from abc import ABC
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .audio_loader import AudioLoader
from .metadata_parser import MetadataParser
from .whisper_runner import WhisperRunner
from .transcript_writer import TranscriptWriter
from .async_processor import run_transcription_async
from ..models.transcript_segment import TranscriptSegment
from ..models.transcription_log import TranscriptionLog


class TranscriptionService(ABC):
    """
    Abstract base class for audio transcription services.

    Defines the interface for transcribing audio files and managing
    transcription results with optional speaker diarization.
    """

    def __init__(self, model_name: str = "large-v3", enable_diarization: bool = False):
        """
        Initialize the transcription service.

        Args:
            model_name: WhisperX model to use (default: "large-v3")
            enable_diarization: Whether to perform speaker diarization
        """
        self.model_name = model_name
        self.enable_diarization = enable_diarization
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize components
        self.audio_loader = AudioLoader()
        self.metadata_parser = MetadataParser()
        self.whisper_runner = WhisperRunner(model_name)
        self.transcript_writer = TranscriptWriter()

    def _create_transcript_result(self, segments: List[TranscriptSegment],
                                log: TranscriptionLog) -> Dict[str, Any]:
        """
        Create standardized transcript result dictionary.

        Args:
            segments: List of transcript segments
            log: Transcription log entry

        Returns:
            Dictionary with transcript data in standard format
        """
        return {
            "transcript_path": None,  # To be set by caller
            "log_path": None,         # To be set by caller
            "segments": [self._segment_to_dict(segment) for segment in segments],
            "log": self._log_to_dict(log)
        }

    def _segment_to_dict(self, segment: TranscriptSegment) -> Dict[str, Any]:
        """Convert TranscriptSegment to dictionary."""
        result = {
            "start_time": segment.start_time,
            "end_time": segment.end_time,
            "text": segment.text
        }

        if segment.speaker_label is not None:
            result["speaker_label"] = segment.speaker_label

        if segment.words:
            result["words"] = [
                {
                    "word": word.word,
                    "start": word.start,
                    "end": word.end,
                    "confidence": word.confidence
                }
                for word in segment.words
            ]

        return result

    def _log_to_dict(self, log: TranscriptionLog) -> Dict[str, Any]:
        """Convert TranscriptionLog to dictionary."""
        return {
            "timestamp": log.timestamp,
            "runtime": log.runtime,
            "model_name": log.model_name,
            "accuracy_metrics": log.accuracy_metrics,
            "errors": log.errors
        }

    def _save_transcript_json(self, result: Dict[str, Any], output_path: Path) -> None:
        """
        Save transcript result to JSON file.

        Args:
            result: Transcript result dictionary
            output_path: Path to save the JSON file
        """
        result["transcript_path"] = str(output_path)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Transcript saved to {output_path}")

    def _save_log(self, log: TranscriptionLog, log_path: Path) -> None:
        """
        Save transcription log to file.

        Args:
            log: Transcription log entry
            log_path: Path to save the log
        """
        log_data = self._log_to_dict(log)
        log_data["transcript_path"] = str(log_path.parent / "transcript.json")

        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Transcription log saved to {log_path}")

    def _validate_audio_file(self, audio_path: Path) -> None:
        """
        Validate that audio file exists and is accessible.

        Args:
            audio_path: Path to audio file

        Raises:
            FileNotFoundError: If audio file doesn't exist
            ValueError: If file is not a valid audio file
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if not audio_path.is_file():
            raise ValueError(f"Path is not a file: {audio_path}")

        # Basic file extension check
        valid_extensions = {'.wav', '.mp3', '.flac', '.m4a', '.ogg'}
        if audio_path.suffix.lower() not in valid_extensions:
            self.logger.warning(f"Unexpected audio file extension: {audio_path.suffix}")

    def _load_metadata(self, metadata_path: Optional[Path]) -> Optional[Dict[str, Any]]:
        """
        Load session metadata from JSON file.

        Args:
            metadata_path: Path to metadata JSON file

        Returns:
            Metadata dictionary or None if no path provided
        """
        if not metadata_path:
            return None

        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load metadata from {metadata_path}: {e}")
            return None

    async def transcribe_audio(self, audio_path: Path, metadata_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Transcribe an audio file using WhisperX.

        Args:
            audio_path: Path to the audio file to transcribe
            metadata_path: Optional path to session metadata JSON

        Returns:
            Dictionary containing transcription results and paths
        """
        try:
            self.logger.info(f"Starting transcription for: {audio_path}")

            # Validate audio file
            self._validate_audio_file(audio_path)

            # Load metadata if provided
            metadata = None
            session_info = None
            if metadata_path:
                metadata = self.metadata_parser.load_metadata(metadata_path)
                session_info = self.metadata_parser.extract_session_info(metadata)

            # Extract language from metadata or default to English
            language = "en"
            if metadata and "language" in metadata:
                language = metadata["language"]

            # Run transcription in thread pool
            segments, log = await run_transcription_async(
                self.whisper_runner.transcribe_audio,
                audio_path,
                language
            )

            # Generate output paths
            output_dir = audio_path.parent
            base_name = audio_path.stem
            transcript_path = output_dir / f"{base_name}_transcript.json"
            log_path = output_dir / f"{base_name}_transcription.log"

            # Write transcript
            self.transcript_writer.write_transcript(segments, log, transcript_path, session_info)

            # Write log
            self.transcript_writer.write_log_only(log, log_path)

            # Build result
            result = self._create_transcript_result(segments, log)
            result["transcript_path"] = str(transcript_path)
            result["log_path"] = str(log_path)

            self.logger.info(f"Transcription completed successfully: {transcript_path}")
            return result

        except Exception as e:
            error_msg = f"Transcription failed for {audio_path}: {e}"
            self.logger.error(error_msg)

            # Create error result
            error_log = TranscriptionLog.create_log(
                model_name=self.model_name,
                start_time=datetime.now(),
                accuracy_metrics={},
                errors=[str(e)]
            )

            return {
                "transcript_path": None,
                "log_path": None,
                "segments": [],
                "log": self._log_to_dict(error_log),
                "error": str(e)
            }