"""
Audio file loader for transcription operations.

Handles loading and basic validation of audio files in various formats,
ensuring they are suitable for WhisperX processing.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple, Any
import numpy as np

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    librosa = None


class AudioLoader:
    """
    Loads and validates audio files for transcription.

    Handles various audio formats and ensures they meet WhisperX requirements
    (16kHz mono format preferred).
    """

    def __init__(self):
        """Initialize the audio loader."""
        self.logger = logging.getLogger(self.__class__.__name__)

        if not LIBROSA_AVAILABLE:
            self.logger.warning("librosa not available. Audio loading may be limited.")

    def load_audio(self, audio_path: Path, target_sample_rate: int = 16000) -> Tuple[np.ndarray, int]:
        """
        Load audio file and resample to target rate if needed.

        Args:
            audio_path: Path to the audio file
            target_sample_rate: Target sample rate (default: 16000 for WhisperX)

        Returns:
            Tuple of (audio_array, sample_rate)

        Raises:
            FileNotFoundError: If audio file doesn't exist
            ValueError: If audio format is unsupported
            RuntimeError: If audio loading fails
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            self.logger.info(f"Loading audio file: {audio_path}")

            if LIBROSA_AVAILABLE:
                # Use librosa for robust audio loading
                audio, sample_rate = librosa.load(str(audio_path), sr=target_sample_rate, mono=True)
            else:
                # Fallback to basic numpy/scipy if available
                try:
                    from scipy.io import wavfile
                    sample_rate, audio = wavfile.read(str(audio_path))

                    # Convert to float32 and mono if needed
                    if audio.dtype != np.float32:
                        audio = audio.astype(np.float32)

                    if audio.ndim > 1:
                        audio = np.mean(audio, axis=1)  # Convert to mono

                    # Resample if needed
                    if sample_rate != target_sample_rate:
                        audio = self._resample_audio(audio, sample_rate, target_sample_rate)
                        sample_rate = target_sample_rate

                except ImportError:
                    raise RuntimeError("Neither librosa nor scipy available for audio loading")

            # Validate loaded audio
            self._validate_audio_data(audio, sample_rate)

            self.logger.info(f"Successfully loaded audio: {len(audio)} samples at {sample_rate}Hz")
            return audio, sample_rate

        except Exception as e:
            error_msg = f"Failed to load audio file {audio_path}: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def _resample_audio(self, audio: np.ndarray, original_rate: int, target_rate: int) -> np.ndarray:
        """
        Resample audio to target sample rate.

        Args:
            audio: Audio array
            original_rate: Original sample rate
            target_rate: Target sample rate

        Returns:
            Resampled audio array
        """
        if LIBROSA_AVAILABLE:
            return librosa.resample(audio, orig_sr=original_rate, target_sr=target_rate)
        else:
            # Simple linear interpolation fallback (not ideal but works)
            ratio = target_rate / original_rate
            new_length = int(len(audio) * ratio)
            return np.interp(
                np.linspace(0, len(audio) - 1, new_length),
                np.arange(len(audio)),
                audio
            )

    def _validate_audio_data(self, audio: np.ndarray, sample_rate: int) -> None:
        """
        Validate loaded audio data.

        Args:
            audio: Audio array
            sample_rate: Sample rate

        Raises:
            ValueError: If audio data is invalid
        """
        if len(audio) == 0:
            raise ValueError("Audio file is empty")

        if sample_rate <= 0:
            raise ValueError(f"Invalid sample rate: {sample_rate}")

        # Check for minimum duration (WhisperX needs at least ~0.1 seconds)
        min_samples = int(0.1 * sample_rate)
        if len(audio) < min_samples:
            raise ValueError(f"Audio too short: {len(audio)} samples < {min_samples} required")

        # Check for valid audio range
        if np.max(np.abs(audio)) == 0:
            raise ValueError("Audio appears to be silent (all zeros)")

        # Warn about very long audio
        max_duration_hours = 2  # Based on plan.md constraints
        max_samples = max_duration_hours * 3600 * sample_rate
        if len(audio) > max_samples:
            duration_hours = len(audio) / (sample_rate * 3600)
            self.logger.warning(f"Audio duration ({duration_hours:.1f}h) exceeds recommended limit ({max_duration_hours}h)")

    def get_audio_info(self, audio_path: Path) -> Optional[Dict[str, Any]]:
        """
        Get basic information about an audio file without loading it fully.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with audio info or None if unable to read
        """
        try:
            if LIBROSA_AVAILABLE:
                info = librosa.get_duration(filename=str(audio_path))
                return {
                    "duration_seconds": info,
                    "file_size_bytes": audio_path.stat().st_size,
                    "file_format": audio_path.suffix
                }
        except Exception as e:
            self.logger.warning(f"Could not get audio info for {audio_path}: {e}")

        return None