"""
Metadata parser for transcription operations.

Loads and validates session metadata JSON files, extracting relevant
information for transcription processing and logging.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class MetadataParser:
    """
    Parses session metadata for transcription operations.

    Handles loading, validation, and extraction of session metadata
    that accompanies audio files for transcription.
    """

    def __init__(self):
        """Initialize the metadata parser."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def load_metadata(self, metadata_path: Path) -> Dict[str, Any]:
        """
        Load and parse session metadata from JSON file.

        Args:
            metadata_path: Path to the metadata JSON file

        Returns:
            Parsed metadata dictionary

        Raises:
            FileNotFoundError: If metadata file doesn't exist
            ValueError: If metadata is invalid or malformed
        """
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

        try:
            self.logger.info(f"Loading metadata from: {metadata_path}")

            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # Validate metadata structure
            self._validate_metadata(metadata)

            self.logger.info("Successfully loaded and validated metadata")
            return metadata

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in metadata file {metadata_path}: {e}"
            self.logger.error(error_msg)
            raise ValueError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to load metadata from {metadata_path}: {e}"
            self.logger.error(error_msg)
            raise ValueError(error_msg) from e

    def _validate_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Validate metadata structure and required fields.

        Args:
            metadata: Metadata dictionary to validate

        Raises:
            ValueError: If metadata is invalid
        """
        if not isinstance(metadata, dict):
            raise ValueError("Metadata must be a JSON object")

        # Check for essential fields (these may vary based on session format)
        # For now, we'll be permissive but log warnings for missing fields

        recommended_fields = [
            'session_id', 'start_time', 'end_time', 'guild_id',
            'channel_id', 'participants', 'audio_format'
        ]

        missing_fields = []
        for field in recommended_fields:
            if field not in metadata:
                missing_fields.append(field)

        if missing_fields:
            self.logger.warning(f"Metadata missing recommended fields: {missing_fields}")

        # Validate timestamp fields if present
        for time_field in ['start_time', 'end_time']:
            if time_field in metadata:
                try:
                    # Try to parse as ISO datetime
                    datetime.fromisoformat(metadata[time_field].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    self.logger.warning(f"Invalid timestamp format for {time_field}: {metadata[time_field]}")

    def extract_session_info(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key session information for transcription logging.

        Args:
            metadata: Full metadata dictionary

        Returns:
            Dictionary with extracted session information
        """
        session_info = {
            'session_id': metadata.get('session_id', 'unknown'),
            'guild_id': metadata.get('guild_id'),
            'channel_id': metadata.get('channel_id'),
            'participants': metadata.get('participants', []),
            'start_time': metadata.get('start_time'),
            'end_time': metadata.get('end_time'),
            'audio_format': metadata.get('audio_format', {}),
            'duration_seconds': self._calculate_duration(metadata)
        }

        return session_info

    def _calculate_duration(self, metadata: Dict[str, Any]) -> Optional[float]:
        """
        Calculate session duration from metadata timestamps.

        Args:
            metadata: Metadata dictionary

        Returns:
            Duration in seconds or None if cannot calculate
        """
        try:
            start_time = metadata.get('start_time')
            end_time = metadata.get('end_time')

            if start_time and end_time:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                return (end_dt - start_dt).total_seconds()

        except (ValueError, AttributeError, TypeError):
            pass

        return None

    def get_transcription_context(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract context information useful for transcription processing.

        Args:
            metadata: Full metadata dictionary

        Returns:
            Dictionary with transcription context
        """
        context = {
            'expected_speakers': len(metadata.get('participants', [])),
            'audio_channels': metadata.get('audio_format', {}).get('channels', 1),
            'audio_sample_rate': metadata.get('audio_format', {}).get('sample_rate', 16000),
            'session_type': metadata.get('session_type', 'voice_channel'),
            'language': metadata.get('language', 'en'),  # Default to English
        }

        # Add participant info for potential speaker mapping
        participants = metadata.get('participants', [])
        if participants:
            context['participant_ids'] = [p.get('user_id') for p in participants if isinstance(p, dict)]
            context['participant_names'] = [p.get('username', p.get('name', 'Unknown'))
                                          for p in participants if isinstance(p, dict)]

        return context