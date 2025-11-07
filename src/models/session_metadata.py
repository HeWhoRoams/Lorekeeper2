from dataclasses import dataclass
from typing import List

@dataclass
class SessionMetadata:
    guild_id: str
    channel_id: str
    participants: List[str]
    start_time: str  # ISO datetime string
    end_time: str    # ISO datetime string
    duration: float
    file_path: str