"""
Transcript JSON Schema Validator
Validates transcript.json output against required schema for audio transcription.
"""
import json
from typing import Any, Dict, List

class TranscriptValidator:
    REQUIRED_TOP_LEVEL_KEYS = ["metadata", "segments", "log"]
    REQUIRED_METADATA_KEYS = ["created_at", "format_version", "transcription_model", "total_segments", "total_duration"]
    REQUIRED_SEGMENT_KEYS = ["start_time", "end_time", "text"]
    REQUIRED_LOG_KEYS = ["timestamp", "runtime_seconds", "model_name", "accuracy_metrics", "errors", "successful"]

    @staticmethod
    def validate_transcript(transcript: Dict[str, Any]) -> List[str]:
        errors = []
        # Top-level keys
        for key in TranscriptValidator.REQUIRED_TOP_LEVEL_KEYS:
            if key not in transcript:
                errors.append(f"Missing top-level key: {key}")
        # Metadata
        metadata = transcript.get("metadata", {})
        for key in TranscriptValidator.REQUIRED_METADATA_KEYS:
            if key not in metadata:
                errors.append(f"Missing metadata key: {key}")
        # Segments
        segments = transcript.get("segments", [])
        if not isinstance(segments, list):
            errors.append("Segments must be a list")
        for i, segment in enumerate(segments):
            for key in TranscriptValidator.REQUIRED_SEGMENT_KEYS:
                if key not in segment:
                    errors.append(f"Segment {i} missing key: {key}")
            if segment.get("start_time", 0) >= segment.get("end_time", 0):
                errors.append(f"Segment {i} start_time >= end_time")
        # Log
        log = transcript.get("log", {})
        for key in TranscriptValidator.REQUIRED_LOG_KEYS:
            if key not in log:
                errors.append(f"Missing log key: {key}")
        return errors

    @staticmethod
    def validate_file(path: str) -> List[str]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                transcript = json.load(f)
            return TranscriptValidator.validate_transcript(transcript)
        except Exception as e:
            return [f"Failed to load or parse transcript file: {e}"]
