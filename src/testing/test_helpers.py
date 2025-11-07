"""
Test helpers and utilities for transcription testing.
Provides reusable functions for test setup, validation, and assertions.
"""
import json
from pathlib import Path
from typing import Dict, Any, List


def load_json_fixture(fixture_path: str) -> Dict[str, Any]:
    """Load a JSON fixture file for testing."""
    with open(fixture_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def compare_transcripts(actual: Dict[str, Any], expected: Dict[str, Any], tolerance_ms: float = 250) -> List[str]:
    """
    Compare actual and expected transcripts, returning list of differences.
    
    Args:
        actual: Actual transcript dict
        expected: Expected transcript dict
        tolerance_ms: Acceptable timestamp difference in milliseconds
        
    Returns:
        List of difference descriptions (empty if match)
    """
    differences = []
    
    # Check segment count
    actual_segments = actual.get("segments", [])
    expected_segments = expected.get("segments", [])
    
    if len(actual_segments) != len(expected_segments):
        differences.append(f"Segment count mismatch: {len(actual_segments)} vs {len(expected_segments)}")
        return differences
    
    # Compare each segment
    for i, (actual_seg, expected_seg) in enumerate(zip(actual_segments, expected_segments)):
        # Check text
        if actual_seg.get("text", "").strip() != expected_seg.get("text", "").strip():
            differences.append(f"Segment {i} text mismatch: '{actual_seg.get('text')}' vs '{expected_seg.get('text')}'")
        
        # Check timestamps (with tolerance)
        actual_start = actual_seg.get("start_time", 0)
        expected_start = expected_seg.get("start_time", 0)
        if abs(actual_start - expected_start) > (tolerance_ms / 1000):
            differences.append(f"Segment {i} start_time off by {abs(actual_start - expected_start) * 1000:.0f}ms")
        
        actual_end = actual_seg.get("end_time", 0)
        expected_end = expected_seg.get("end_time", 0)
        if abs(actual_end - expected_end) > (tolerance_ms / 1000):
            differences.append(f"Segment {i} end_time off by {abs(actual_end - expected_end) * 1000:.0f}ms")
    
    return differences


def calculate_word_error_rate(actual_text: str, expected_text: str) -> float:
    """
    Calculate Word Error Rate (WER) between actual and expected text.
    
    Returns:
        WER as float (0.0 = perfect match, 1.0 = completely different)
    """
    actual_words = actual_text.lower().split()
    expected_words = expected_text.lower().split()
    
    if not expected_words:
        return 0.0 if not actual_words else 1.0
    
    # Simple edit distance calculation (Levenshtein for words)
    m, n = len(actual_words), len(expected_words)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if actual_words[i-1] == expected_words[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    
    return dp[m][n] / n


def validate_audio_file(audio_path: str, expected_sample_rate: int = 16000, expected_duration: float = None) -> List[str]:
    """
    Validate audio file format and properties.
    
    Returns:
        List of validation errors (empty if valid)
    """
    import wave
    errors = []
    
    try:
        with wave.open(audio_path, 'rb') as wav:
            sample_rate = wav.getframerate()
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            frames = wav.getnframes()
            duration = frames / sample_rate
            
            if sample_rate != expected_sample_rate:
                errors.append(f"Sample rate {sample_rate} != expected {expected_sample_rate}")
            
            if channels != 1:
                errors.append(f"Expected mono audio, got {channels} channels")
            
            if sample_width != 2:
                errors.append(f"Expected 16-bit audio, got {sample_width * 8}-bit")
            
            if expected_duration is not None and abs(duration - expected_duration) > 0.5:
                errors.append(f"Duration {duration:.2f}s != expected {expected_duration:.2f}s")
    
    except Exception as e:
        errors.append(f"Failed to read audio file: {e}")
    
    return errors
