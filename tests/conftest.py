"""
pytest configuration and shared fixtures for transcription testing.
"""
import pytest
import json
from pathlib import Path
from typing import Dict, Any

# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"
AUDIO_DIR = FIXTURES_DIR / "audio"
METADATA_DIR = FIXTURES_DIR / "metadata"
EXPECTED_OUTPUTS_DIR = FIXTURES_DIR / "expected_outputs"


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def audio_dir() -> Path:
    """Return path to test audio fixtures directory."""
    return AUDIO_DIR


@pytest.fixture
def metadata_dir() -> Path:
    """Return path to test metadata fixtures directory."""
    return METADATA_DIR


@pytest.fixture
def expected_outputs_dir() -> Path:
    """Return path to expected outputs fixtures directory."""
    return EXPECTED_OUTPUTS_DIR


@pytest.fixture
def valid_metadata() -> Dict[str, Any]:
    """Load valid session metadata fixture."""
    with open(METADATA_DIR / "valid_metadata.json", 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture
def single_speaker_expected() -> Dict[str, Any]:
    """Load expected transcript for single speaker audio."""
    with open(EXPECTED_OUTPUTS_DIR / "single_speaker_transcript.json", 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture
def single_speaker_audio(audio_dir: Path) -> Path:
    """Return path to single speaker test audio."""
    audio_path = audio_dir / "single_speaker_10s.wav"
    if not audio_path.exists():
        pytest.skip(f"Test audio not found: {audio_path}")
    return audio_path


@pytest.fixture
def multi_speaker_audio(audio_dir: Path) -> Path:
    """Return path to multi-speaker test audio."""
    audio_path = audio_dir / "multi_speaker_30s.wav"
    if not audio_path.exists():
        pytest.skip(f"Test audio not found: {audio_path}")
    return audio_path


@pytest.fixture
def corrupted_audio(audio_dir: Path) -> Path:
    """Return path to corrupted test audio."""
    audio_path = audio_dir / "corrupted.wav"
    if not audio_path.exists():
        pytest.skip(f"Test audio not found: {audio_path}")
    return audio_path


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create temporary directory for test outputs."""
    output_dir = tmp_path / "transcription_output"
    output_dir.mkdir(exist_ok=True)
    return output_dir
