"""
Transcription log model for tracking transcription operations.

Records metadata about transcription runs including timing, model used,
performance metrics, and any errors encountered.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TranscriptionLog:
    """
    Log entry for a transcription operation.

    Tracks the execution details, performance metrics, and any errors
    that occurred during audio transcription processing.
    """
    timestamp: str  # ISO datetime string when transcription started
    runtime: float  # Total runtime in seconds
    model_name: str  # WhisperX model name (e.g., "large-v3")
    accuracy_metrics: Dict[str, float]  # Performance metrics (confidence scores, etc.)
    errors: List[str]  # Error messages (empty if successful)

    @classmethod
    def create_log(cls, model_name: str, start_time: datetime,
                   accuracy_metrics: Optional[Dict[str, float]] = None,
                   errors: Optional[List[str]] = None) -> 'TranscriptionLog':
        """
        Create a new transcription log entry.

        Args:
            model_name: Name of the WhisperX model used
            start_time: When transcription began
            accuracy_metrics: Optional performance metrics
            errors: Optional list of error messages

        Returns:
            New TranscriptionLog instance
        """
        runtime = (datetime.now() - start_time).total_seconds()

        return cls(
            timestamp=start_time.isoformat(),
            runtime=runtime,
            model_name=model_name,
            accuracy_metrics=accuracy_metrics or {},
            errors=errors or []
        )

    @property
    def was_successful(self) -> bool:
        """Check if transcription completed without errors."""
        return len(self.errors) == 0

    @property
    def average_confidence(self) -> Optional[float]:
        """Calculate average confidence score if available."""
        if not self.accuracy_metrics:
            return None

        confidence_values = [v for k, v in self.accuracy_metrics.items()
                           if 'confidence' in k.lower()]
        return sum(confidence_values) / len(confidence_values) if confidence_values else None