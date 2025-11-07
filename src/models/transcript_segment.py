"""
Transcript segment model for audio transcription results.

Represents a segment of transcribed audio with timestamps, text, and optional
speaker identification and word-level alignment data.
"""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class WordAlignment:
    """Word-level alignment data within a transcript segment."""
    word: str
    start: float  # Start time in seconds
    end: float    # End time in seconds
    confidence: float  # Confidence score (0.0 to 1.0)


@dataclass
class TranscriptSegment:
    """
    A segment of transcribed audio.

    Represents a continuous portion of transcribed speech with timing,
    text content, and optional speaker identification.
    """
    start_time: float  # Start time in seconds
    end_time: float    # End time in seconds
    text: str          # Transcribed text for this segment
    speaker_label: Optional[str] = None  # Speaker identifier (None if diarization disabled)
    words: Optional[List[WordAlignment]] = None  # Word-level alignment data

    def __post_init__(self):
        """Validate segment data after initialization."""
        if self.start_time >= self.end_time:
            raise ValueError(f"start_time ({self.start_time}) must be less than end_time ({self.end_time})")

        if self.words:
            # Validate word alignments are within segment boundaries
            for word in self.words:
                if word.start < self.start_time or word.end > self.end_time:
                    raise ValueError(f"Word '{word.word}' timing ({word.start}-{word.end}) "
                                   f"outside segment boundaries ({self.start_time}-{self.end_time})")

    @property
    def duration(self) -> float:
        """Calculate segment duration in seconds."""
        return self.end_time - self.start_time