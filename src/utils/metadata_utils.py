import json
import os
from datetime import datetime
from typing import List

from src.models.session_metadata import SessionMetadata

def save_metadata(metadata: SessionMetadata, output_dir: str) -> str:
    """
    Save session metadata to JSON file.
    Returns the file path.
    """
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.fromisoformat(metadata.start_time).strftime('%Y%m%d_%H%M%S')
    file_path = f"{output_dir}/session_{timestamp}_metadata.json"

    data = {
        "guild_id": metadata.guild_id,
        "channel_id": metadata.channel_id,
        "participants": metadata.participants,
        "start_time": metadata.start_time,
        "end_time": metadata.end_time,
        "duration": metadata.duration,
        "file_path": metadata.file_path
    }

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

    return file_path

def load_metadata(file_path: str) -> SessionMetadata:
    """
    Load session metadata from JSON file.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)

    return SessionMetadata(
        guild_id=data["guild_id"],
        channel_id=data["channel_id"],
        participants=data["participants"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        duration=data["duration"],
        file_path=data["file_path"]
    )