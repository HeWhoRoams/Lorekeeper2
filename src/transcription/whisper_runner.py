"""
WhisperX transcription runner for audio processing.

Handles the core WhisperX transcription pipeline including model loading,
audio processing, alignment, and result formatting.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime

from .model_manager import get_model_manager
from .audio_loader import AudioLoader
from ..models.transcript_segment import TranscriptSegment, WordAlignment
from ..models.transcription_log import TranscriptionLog


class WhisperRunner:
    """
    Runs WhisperX transcription on audio files.

    Manages the complete WhisperX pipeline: transcription, alignment,
    and result processing with proper error handling.
    """

    def __init__(self, model_name: str = "large-v3"):
        """
        Initialize the WhisperX runner.

        Args:
            model_name: WhisperX model to use (default: "large-v3")
        """
        self.model_name = model_name
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model_manager = get_model_manager()
        self.audio_loader = AudioLoader()

    def transcribe_audio(self, audio_path: Path,
                        language: str = "en") -> Tuple[List[TranscriptSegment], TranscriptionLog]:
        """
        Transcribe an audio file using WhisperX.

        Args:
            audio_path: Path to the audio file
            language: Language code for transcription

        Returns:
            Tuple of (transcript_segments, transcription_log)

        Raises:
            RuntimeError: If transcription fails
        """
        start_time = datetime.now()

        try:
            self.logger.info(f"Starting WhisperX transcription: {audio_path}")

            # Load and validate audio
            audio, sample_rate = self.audio_loader.load_audio(audio_path)

            # Load WhisperX model
            model = self.model_manager.load_model(self.model_name)

            # Run transcription
            self.logger.info("Running WhisperX transcription...")
            result = model.transcribe(audio, language=language)

            # Load alignment model for precise timestamps
            align_model, metadata = self.model_manager.load_align_model(language)

            # Align transcription results
            self.logger.info("Aligning transcription results...")
            aligned_result = whisperx.align(
                result["segments"],
                align_model,
                metadata,
                audio,
                device=self.model_manager._get_device_and_dtype()[0]
            )

            # Convert to our segment format
            segments = self._convert_to_segments(aligned_result)

            # Calculate accuracy metrics
            accuracy_metrics = self._calculate_accuracy_metrics(result, aligned_result)

            # Create log entry
            log = TranscriptionLog.create_log(
                model_name=self.model_name,
                start_time=start_time,
                accuracy_metrics=accuracy_metrics,
                errors=[]
            )

            self.logger.info(f"Transcription completed successfully in {log.runtime:.2f}s")
            return segments, log

        except Exception as e:
            error_msg = f"WhisperX transcription failed: {e}"
            self.logger.error(error_msg)

            # Create error log
            error_log = TranscriptionLog.create_log(
                model_name=self.model_name,
                start_time=start_time,
                accuracy_metrics={},
                errors=[str(e)]
            )

            raise RuntimeError(error_msg) from e

    def _convert_to_segments(self, aligned_result: Dict[str, Any]) -> List[TranscriptSegment]:
        """
        Convert WhisperX aligned results to TranscriptSegment objects.

        Args:
            aligned_result: Aligned transcription result from WhisperX

        Returns:
            List of TranscriptSegment objects
        """
        segments = []

        for segment_data in aligned_result["segments"]:
            # Extract word alignments if available
            words = None
            if "words" in segment_data:
                words = [
                    WordAlignment(
                        word=word.get("word", ""),
                        start=word.get("start", 0.0),
                        end=word.get("end", 0.0),
                        confidence=word.get("confidence", 0.0)
                    )
                    for word in segment_data["words"]
                ]

            # Create segment
            segment = TranscriptSegment(
                start_time=segment_data.get("start", 0.0),
                end_time=segment_data.get("end", 0.0),
                text=segment_data.get("text", "").strip(),
                words=words
            )

            segments.append(segment)

        return segments

    def _calculate_accuracy_metrics(self, raw_result: Dict[str, Any],
                                  aligned_result: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate accuracy metrics from transcription results.

        Args:
            raw_result: Raw WhisperX transcription result
            aligned_result: Aligned result with word timestamps

        Returns:
            Dictionary of accuracy metrics
        """
        metrics = {}

        # Average confidence from raw result
        if "segments" in raw_result:
            confidences = []
            for segment in raw_result["segments"]:
                if "avg_logprob" in segment:
                    # Convert log probability to confidence (rough approximation)
                    confidence = 1.0 / (1.0 + np.exp(-segment["avg_logprob"]))
                    confidences.append(confidence)

            if confidences:
                metrics["average_confidence"] = float(np.mean(confidences))
                metrics["min_confidence"] = float(np.min(confidences))
                metrics["max_confidence"] = float(np.max(confidences))

        # Word-level metrics from alignment
        if "segments" in aligned_result:
            total_words = 0
            total_confidence = 0.0

            for segment in aligned_result["segments"]:
                if "words" in segment:
                    for word in segment["words"]:
                        if "confidence" in word:
                            total_words += 1
                            total_confidence += word["confidence"]

            if total_words > 0:
                metrics["word_level_confidence"] = total_confidence / total_words
                metrics["total_words"] = total_words

        return metrics

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current WhisperX model.

        Returns:
            Dictionary with model information
        """
        return self.model_manager.get_model_info(self.model_name) or {}


# Import whisperx here to avoid circular imports
try:
    import whisperx
except ImportError:
    whisperx = None