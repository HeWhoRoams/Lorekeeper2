"""
Schema and data validators for transcription testing.
Provides validation logic for transcription outputs, metadata, and logs.
"""
from typing import Dict, Any, List


def validate_transcript_schema(transcript: Dict[str, Any]) -> List[str]:
    """
    Validate transcript JSON against expected schema.
    
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Required top-level fields
    required_fields = ["metadata", "segments", "log"]
    for field in required_fields:
        if field not in transcript:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return errors
    
    # Validate metadata
    metadata = transcript["metadata"]
    metadata_fields = ["guild_id", "channel_id", "start_time", "end_time", "sample_rate"]
    for field in metadata_fields:
        if field not in metadata:
            errors.append(f"Missing metadata field: {field}")
    
    # Validate segments
    segments = transcript.get("segments", [])
    if not isinstance(segments, list):
        errors.append("segments must be a list")
    else:
        for i, segment in enumerate(segments):
            segment_fields = ["start_time", "end_time", "speaker", "text"]
            for field in segment_fields:
                if field not in segment:
                    errors.append(f"Segment {i} missing field: {field}")
            
            # Validate timestamps
            if "start_time" in segment and "end_time" in segment:
                if segment["end_time"] <= segment["start_time"]:
                    errors.append(f"Segment {i} end_time must be > start_time")
            
            # Validate words if present
            if "words" in segment:
                for j, word in enumerate(segment["words"]):
                    word_fields = ["word", "start", "end", "confidence"]
                    for field in word_fields:
                        if field not in word:
                            errors.append(f"Segment {i}, word {j} missing field: {field}")
    
    # Validate log
    log = transcript.get("log", {})
    log_fields = ["model", "language", "duration"]
    for field in log_fields:
        if field not in log:
            errors.append(f"Missing log field: {field}")
    
    return errors


def validate_metadata_schema(metadata: Dict[str, Any]) -> List[str]:
    """
    Validate session metadata JSON against expected schema.
    
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    required_fields = ["guild_id", "channel_id", "start_time", "end_time", "sample_rate", "users"]
    for field in required_fields:
        if field not in metadata:
            errors.append(f"Missing required field: {field}")
    
    # Validate users
    if "users" in metadata:
        users = metadata["users"]
        if not isinstance(users, dict):
            errors.append("users must be a dictionary")
        else:
            for user_id, user_info in users.items():
                if "player" not in user_info:
                    errors.append(f"User {user_id} missing 'player' field")
                if "character" not in user_info:
                    errors.append(f"User {user_id} missing 'character' field")
    
    # Validate timestamps
    if "start_time" in metadata and "end_time" in metadata:
        if metadata["end_time"] <= metadata["start_time"]:
            errors.append("end_time must be > start_time")
    
    # Validate sample_rate
    if "sample_rate" in metadata:
        if not isinstance(metadata["sample_rate"], int) or metadata["sample_rate"] <= 0:
            errors.append("sample_rate must be a positive integer")
    
    return errors


def validate_log_entry(log_entry: Dict[str, Any]) -> List[str]:
    """
    Validate transcription log entry against expected schema.
    
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    required_fields = ["date", "begin", "end", "user_id", "player", "character", "event_source", "data"]
    for field in required_fields:
        if field not in log_entry:
            errors.append(f"Missing required field: {field}")
    
    # Validate timestamps
    if "begin" in log_entry and "end" in log_entry:
        if log_entry["end"] < log_entry["begin"]:
            errors.append("end timestamp must be >= begin timestamp")
    
    # Validate data structure
    if "data" in log_entry:
        data = log_entry["data"]
        if not isinstance(data, dict):
            errors.append("data must be a dictionary")
        elif "text" not in data:
            errors.append("data must contain 'text' field")
    
    return errors
