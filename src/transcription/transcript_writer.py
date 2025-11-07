"""
Transcript writer for saving transcription results.

Handles formatting and saving transcription results to JSON files
with proper schema validation and error handling.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.transcript_segment import TranscriptSegment
from ..models.transcription_log import TranscriptionLog


class TranscriptWriter:
    """
    Writes transcription results to JSON files.

    Formats and saves transcript data with proper schema validation,
    ensuring compatibility with downstream processing.
    """

    def __init__(self):
        """Initialize the transcript writer."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def write_transcript(self, segments: List[TranscriptSegment],
                        log: TranscriptionLog,
                        output_path: Path,
                        session_info: Optional[Dict[str, Any]] = None) -> Path:
        """
        Write transcription results to a JSON file.

        Args:
            segments: List of transcript segments
            log: Transcription log entry
            output_path: Path where to save the transcript
            session_info: Optional session metadata

        Returns:
            Path to the written file

        Raises:
            IOError: If writing fails
            ValueError: If data validation fails
        """
        try:
            self.logger.info(f"Writing transcript to: {output_path}")

            # Create output directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Build transcript data structure
            transcript_data = self._build_transcript_data(segments, log, session_info)

            # Validate data before writing
            self._validate_transcript_data(transcript_data)

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Successfully wrote transcript with {len(segments)} segments")
            return output_path

        except Exception as e:
            error_msg = f"Failed to write transcript to {output_path}: {e}"
            self.logger.error(error_msg)
            raise IOError(error_msg) from e

    def _build_transcript_data(self, segments: List[TranscriptSegment],
                             log: TranscriptionLog,
                             session_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Build the complete transcript data structure.

        Args:
            segments: Transcript segments
            log: Transcription log
            session_info: Optional session information

        Returns:
            Complete transcript data dictionary
        """
        # Convert segments to dictionaries
        segments_data = []
        for segment in segments:
            segment_dict = {
                "start_time": segment.start_time,
                "end_time": segment.end_time,
                "text": segment.text
            }

            # Add speaker label if available
            if segment.speaker_label is not None:
                segment_dict["speaker_label"] = segment.speaker_label

            # Add word alignments if available
            if segment.words:
                segment_dict["words"] = [
                    {
                        "word": word.word,
                        "start": word.start,
                        "end": word.end,
                        "confidence": word.confidence
                    }
                    for word in segment.words
                ]

            segments_data.append(segment_dict)

        # Build main transcript structure
        transcript_data = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "format_version": "1.0",
                "transcription_model": log.model_name,
                "total_segments": len(segments),
                "total_duration": self._calculate_total_duration(segments)
            },
            "segments": segments_data,
            "log": {
                "timestamp": log.timestamp,
                "runtime_seconds": log.runtime,
                "model_name": log.model_name,
                "accuracy_metrics": log.accuracy_metrics,
                "errors": log.errors,
                "successful": log.was_successful
            }
        }

        # Add session info if provided
        if session_info:
            transcript_data["session"] = session_info

        return transcript_data

    def _calculate_total_duration(self, segments: List[TranscriptSegment]) -> float:
        """
        Calculate total duration from segments.

        Args:
            segments: List of transcript segments

        Returns:
            Total duration in seconds
        """
        if not segments:
            return 0.0

        return max(segment.end_time for segment in segments)

    def _validate_transcript_data(self, data: Dict[str, Any]) -> None:
        """
        Validate transcript data structure.

        Args:
            data: Transcript data dictionary

        Raises:
            ValueError: If validation fails
        """
        # Check required top-level keys
        required_keys = ["metadata", "segments", "log"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")

        # Validate metadata
        metadata = data["metadata"]
        if not isinstance(metadata.get("total_segments"), int) or metadata["total_segments"] < 0:
            raise ValueError("Invalid total_segments in metadata")

        # Validate segments
        segments = data["segments"]
        if not isinstance(segments, list):
            raise ValueError("Segments must be a list")

        for i, segment in enumerate(segments):
            if not isinstance(segment, dict):
                raise ValueError(f"Segment {i} must be a dictionary")

            required_segment_keys = ["start_time", "end_time", "text"]
            for key in required_segment_keys:
                if key not in segment:
                    raise ValueError(f"Segment {i} missing required key: {key}")

            # Validate timing
            start_time = segment["start_time"]
            end_time = segment["end_time"]
            if not isinstance(start_time, (int, float)) or not isinstance(end_time, (int, float)):
                raise ValueError(f"Segment {i} has invalid timing values")
            if start_time >= end_time:
                raise ValueError(f"Segment {i} start_time >= end_time")

        # Validate log
        log = data["log"]
        if not isinstance(log.get("runtime_seconds"), (int, float)):
            raise ValueError("Invalid runtime_seconds in log")

    def write_log_only(self, log: TranscriptionLog, output_path: Path) -> Path:
        """
        Write only the transcription log to a file.

        Args:
            log: Transcription log entry
            output_path: Path where to save the log

        Returns:
            Path to the written file
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            log_data = {
                "timestamp": log.timestamp,
                "runtime_seconds": log.runtime,
                "model_name": log.model_name,
                "accuracy_metrics": log.accuracy_metrics,
                "errors": log.errors,
                "successful": log.was_successful
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Successfully wrote transcription log to {output_path}")
            return output_path

        except Exception as e:
            error_msg = f"Failed to write log to {output_path}: {e}"
            self.logger.error(error_msg)
            raise IOError(error_msg) from e