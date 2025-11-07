"""
WhisperX model manager for GPU/CPU model loading and management.

Handles WhisperX model initialization with automatic GPU detection and
CPU fallback, providing a clean interface for model operations.
"""

import logging
import torch
from typing import Optional, Any, Dict
import gc

try:
    import whisperx
    WHISPERX_AVAILABLE = True
except ImportError:
    WHISPERX_AVAILABLE = False
    whisperx = None


class ModelManager:
    """
    Manages WhisperX model loading and GPU/CPU resource allocation.

    Provides automatic GPU detection with CPU fallback, model caching,
    and proper resource cleanup.
    """

    def __init__(self):
        """Initialize the model manager."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.loaded_models: Dict[str, Any] = {}
        self._check_whisperx_availability()

    def _check_whisperx_availability(self) -> None:
        """Check if WhisperX is available and log status."""
        if not WHISPERX_AVAILABLE:
            raise ImportError("WhisperX is not installed. Install with: pip install whisperx")

        # Check GPU availability
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"
            self.logger.info(f"GPU available: {gpu_count} device(s), using {gpu_name}")
        else:
            self.logger.info("No GPU available, using CPU mode")

    def _get_device_and_dtype(self) -> tuple:
        """
        Determine the best available device and data type for WhisperX.

        Returns:
            Tuple of (device, dtype) for model loading
        """
        if torch.cuda.is_available():
            # Check available VRAM (need at least 5GB for large models)
            try:
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
                if gpu_memory >= 5.0:
                    self.logger.info(f"GPU available with {gpu_memory:.1f}GB VRAM - using CUDA acceleration")
                    return "cuda", torch.float16
                else:
                    self.logger.warning(f"GPU has only {gpu_memory:.1f}GB VRAM - falling back to CPU")
                    return "cpu", torch.float32
            except Exception as e:
                self.logger.warning(f"Could not check GPU memory: {e}")
                return "cpu", torch.float32
        else:
            return "cpu", torch.float32

    def load_model(self, model_name: str = "large-v3") -> Any:
        """
        Load a WhisperX model with optimal device configuration.

        Args:
            model_name: Name of the WhisperX model to load

        Returns:
            Loaded WhisperX model

        Raises:
            RuntimeError: If model loading fails
        """
        if model_name in self.loaded_models:
            self.logger.info(f"Using cached model: {model_name}")
            return self.loaded_models[model_name]

        try:
            device, dtype = self._get_device_and_dtype()

            self.logger.info(f"Loading WhisperX model '{model_name}' on {device}")

            # Load the model
            model = whisperx.load_model(
                model_name,
                device=device,
                compute_type="float16" if dtype == torch.float16 else "float32",
                language="en",  # Default to English for Discord voice
                asr_options={"suppress_tokens": []}  # Don't suppress any tokens
            )

            # Cache the model
            self.loaded_models[model_name] = model

            self.logger.info(f"Successfully loaded model '{model_name}'")
            return model

        except Exception as e:
            error_msg = f"Failed to load WhisperX model '{model_name}': {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def load_align_model(self, language_code: str = "en") -> Any:
        """
        Load WhisperX alignment model for precise timestamping.

        Args:
            language_code: Language code for alignment model

        Returns:
            Loaded alignment model
        """
        cache_key = f"align_{language_code}"

        if cache_key in self.loaded_models:
            return self.loaded_models[cache_key]

        try:
            device, _ = self._get_device_and_dtype()

            self.logger.info(f"Loading alignment model for language '{language_code}' on {device}")

            align_model, metadata = whisperx.load_align_model(
                language_code=language_code,
                device=device
            )

            # Cache both model and metadata
            self.loaded_models[cache_key] = (align_model, metadata)

            self.logger.info(f"Successfully loaded alignment model for '{language_code}'")
            return align_model, metadata

        except Exception as e:
            error_msg = f"Failed to load alignment model for '{language_code}': {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def unload_model(self, model_name: str) -> None:
        """
        Unload a cached model to free memory.

        Args:
            model_name: Name of the model to unload
        """
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]

            # Force garbage collection
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            self.logger.info(f"Unloaded model: {model_name}")

    def unload_all_models(self) -> None:
        """Unload all cached models."""
        model_names = list(self.loaded_models.keys())
        for name in model_names:
            self.unload_model(name)

        self.logger.info("Unloaded all cached models")

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a loaded model.

        Args:
            model_name: Name of the model

        Returns:
            Dictionary with model information or None if not loaded
        """
        if model_name not in self.loaded_models:
            return None

        model = self.loaded_models[model_name]

        # Basic info - this will vary based on model type
        info = {
            "name": model_name,
            "loaded": True,
            "type": type(model).__name__
        }

        # Try to get device info if available
        if hasattr(model, 'device'):
            info["device"] = str(model.device)

        return info


# Global model manager instance
_model_manager: Optional[ModelManager] = None


def get_model_manager() -> ModelManager:
    """Get the global model manager instance."""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager