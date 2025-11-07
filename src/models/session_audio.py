from dataclasses import dataclass
from typing import Optional

@dataclass
class SessionAudio:
    file_path: str
    format: str = "WAV"
    sample_rate: int = 16000
    channels: int = 1
    bit_depth: int = 16
    duration: Optional[float] = None