"""
Transcription Configuration Management
Provides runtime configuration for transcription options (model, diarization, etc).
"""
import os
from typing import Optional

class TranscriptionConfig:
    def __init__(self):
        self.model_name = os.getenv("TRANSCRIPTION_MODEL", "large-v3")
        self.enable_diarization = os.getenv("TRANSCRIPTION_DIARIZATION", "false").lower() == "true"
        self.hf_auth_token = os.getenv("HF_TOKEN")
        self.min_speakers = int(os.getenv("TRANSCRIPTION_MIN_SPEAKERS", "1"))
        self.max_speakers = int(os.getenv("TRANSCRIPTION_MAX_SPEAKERS", "10"))

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def as_dict(self):
        return {
            "model_name": self.model_name,
            "enable_diarization": self.enable_diarization,
            "hf_auth_token": self.hf_auth_token,
            "min_speakers": self.min_speakers,
            "max_speakers": self.max_speakers,
        }
