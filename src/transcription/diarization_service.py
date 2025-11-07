"""
Speaker diarization service using pyannote.audio.

Provides speaker identification and labeling for multi-speaker audio
transcription, integrating with WhisperX alignment results.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime

try:
    from pyannote.audio import Pipeline
    from pyannote.audio.pipelines.utils.hook import ProgressHook
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False
    Pipeline = None
    ProgressHook = None

from .audio_loader import AudioLoader
from ..models.transcript_segment import TranscriptSegment


class DiarizationService:
    """
    Speaker diarization service using pyannote.audio.

    Identifies different speakers in audio and assigns consistent labels
    to transcription segments for multi-speaker conversations.
    """

    def __init__(self, auth_token: Optional[str] = None, min_speakers: int = 1, max_speakers: int = 10):
        """
        Initialize the diarization service.

        Args:
            auth_token: HuggingFace authentication token for pyannote models
            min_speakers: Minimum number of speakers to detect (default: 1)
            max_speakers: Maximum number of speakers to detect (default: 10)
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.auth_token = auth_token or self._get_auth_token()
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers
        self.pipeline: Optional[Pipeline] = None
        self.audio_loader = AudioLoader()

        if not PYANNOTE_AVAILABLE:
            self.logger.warning("pyannote.audio not available. Speaker diarization will be disabled.")
            return

        try:
            self._initialize_pipeline()
        except Exception as e:
            self.logger.error(f"Failed to initialize diarization pipeline: {e}")
            self.logger.warning("Speaker diarization will be unavailable")

    def _get_auth_token(self) -> Optional[str]:
        """Get HuggingFace authentication token from environment."""
        return os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")

    def _initialize_pipeline(self) -> None:
        """Initialize the pyannote diarization pipeline."""
        if not self.auth_token:
            raise ValueError("HuggingFace authentication token required for pyannote.audio. "
                           "Set HF_TOKEN or HUGGINGFACE_TOKEN environment variable.")

        self.logger.info("Initializing pyannote diarization pipeline...")

        # Use the speaker diarization pipeline
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=self.auth_token
        )

        # Configure pipeline for better performance
        if hasattr(self.pipeline, 'parameters'):
            # Set minimum speaker duration (seconds)
            self.pipeline.parameters.min_speakers = self.min_speakers
            self.pipeline.parameters.max_speakers = self.max_speakers  # Reasonable upper limit

        self.logger.info("Diarization pipeline initialized successfully")

    def diarize_audio(self, audio_path: Path) -> Optional[Dict[str, Any]]:
        """
        Perform speaker diarization on an audio file.

        Args:
            audio_path: Path to the audio file

        Returns:
            Dictionary containing speaker segments or None if diarization fails
        """
        if not self.pipeline:
            self.logger.warning("Diarization pipeline not available")
            return None

        try:
            self.logger.info(f"Starting speaker diarization: {audio_path}")

            # Load audio
            audio, sample_rate = self.audio_loader.load_audio(audio_path)

            # Convert to format expected by pyannote (mono, appropriate sample rate)
            if sample_rate != 16000:
                # Resample if needed
                audio = self.audio_loader.resample_audio(audio, sample_rate, 16000)
                sample_rate = 16000

            # Create waveform dictionary as expected by pyannote
            waveform = {"waveform": np.expand_dims(audio, 0), "sample_rate": sample_rate}

            # Run diarization with progress hook
            with ProgressHook() as hook:
                diarization = self.pipeline(waveform, hook=hook)

            # Convert to our format
            speaker_segments = self._convert_diarization_result(diarization)

            self.logger.info(f"Diarization completed: found {len(set(seg['speaker'] for seg in speaker_segments))} speakers")
            return {"segments": speaker_segments}

        except Exception as e:
            self.logger.error(f"Diarization failed for {audio_path}: {e}")
            return None

    def _convert_diarization_result(self, diarization) -> List[Dict[str, Any]]:
        """
        Convert pyannote diarization result to our segment format.

        Args:
            diarization: Pyannote diarization result

        Returns:
            List of speaker segments with start, end, and speaker labels
        """
        segments = []

        for segment, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "start": segment.start,
                "end": segment.end,
                "speaker": speaker
            })

        # Sort by start time
        segments.sort(key=lambda x: x["start"])

        return segments

    def assign_speakers_to_segments(self, transcript_segments: List[TranscriptSegment],
                                  diarization_result: Dict[str, Any]) -> List[TranscriptSegment]:
        """
        Assign speaker labels to transcript segments based on diarization results.

        Creates new TranscriptSegment instances with speaker labels assigned based on
        temporal overlap with diarization results. Input segments are not modified.

        Args:
            transcript_segments: List of transcript segments from WhisperX
            diarization_result: Diarization result with speaker segments

        Returns:
            New list of TranscriptSegment instances with speaker labels assigned
        """
        if not diarization_result or "segments" not in diarization_result:
            self.logger.warning("No diarization results available for speaker assignment")
            return transcript_segments

        speaker_segments = diarization_result["segments"]
        updated_segments = []

        for transcript_seg in transcript_segments:
            # Find overlapping speaker segments
            overlapping_speakers = self._find_overlapping_speakers(
                transcript_seg.start_time,
                transcript_seg.end_time,
                speaker_segments
            )

            # Create a new segment with speaker label assigned
            speaker_label = None
            if overlapping_speakers:
                # Assign the speaker with the most overlap
                speaker_label = max(overlapping_speakers.items(), key=lambda x: x[1])[0]

            # Create new TranscriptSegment instance to avoid mutating input
            new_segment = TranscriptSegment(
                start_time=transcript_seg.start_time,
                end_time=transcript_seg.end_time,
                text=transcript_seg.text,
                speaker_label=speaker_label,
                words=transcript_seg.words
            )

            updated_segments.append(new_segment)

        return updated_segments

    def _find_overlapping_speakers(self, start_time: float, end_time: float,
                                 speaker_segments: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Find speakers that overlap with the given time range.

        Args:
            start_time: Start time of the segment
            end_time: End time of the segment
            speaker_segments: List of speaker segments from diarization

        Returns:
            Dictionary mapping speaker labels to overlap duration
        """
        overlaps = {}

        for speaker_seg in speaker_segments:
            speaker_start = speaker_seg["start"]
            speaker_end = speaker_seg["end"]
            speaker_label = speaker_seg["speaker"]

            # Calculate overlap
            overlap_start = max(start_time, speaker_start)
            overlap_end = min(end_time, speaker_end)
            overlap_duration = max(0, overlap_end - overlap_start)

            if overlap_duration > 0:
                overlaps[speaker_label] = overlaps.get(speaker_label, 0) + overlap_duration

        return overlaps

    def validate_diarization_result(self, diarization_result: Optional[Dict[str, Any]]) -> bool:
        """
        Validate that diarization results are usable.

        Args:
            diarization_result: Diarization result to validate

        Returns:
            True if results are valid and usable
        """
        if not diarization_result or "segments" not in diarization_result:
            return False

        segments = diarization_result["segments"]
        if not segments:
            return False

        # Check that segments have required fields and valid timing
        for segment in segments:
            if not all(key in segment for key in ["start", "end", "speaker"]):
                return False
            if segment["start"] >= segment["end"]:
                return False

        return True

    def get_speaker_summary(self, diarization_result: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Generate a summary of speakers from diarization results.

        Args:
            diarization_result: Diarization result

        Returns:
            Dictionary with speaker statistics or None
        """
        if not self.validate_diarization_result(diarization_result):
            return None

        segments = diarization_result["segments"]
        speakers = {}
        total_duration = 0

        for segment in segments:
            speaker = segment["speaker"]
            duration = segment["end"] - segment["start"]
            total_duration += duration

            if speaker not in speakers:
                speakers[speaker] = {"duration": 0, "segments": 0}

            speakers[speaker]["duration"] += duration
            speakers[speaker]["segments"] += 1

        return {
            "total_speakers": len(speakers),
            "total_duration": total_duration,
            "speakers": speakers
        }