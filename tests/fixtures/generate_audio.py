"""
Generate synthetic test audio files for transcription testing.

This script creates WAV files with synthesized speech for testing purposes.
Requires pyttsx3 for text-to-speech synthesis (optional).
"""
import wave
import struct
import math
from pathlib import Path


def generate_silent_audio(output_path: str, duration_seconds: float, sample_rate: int = 16000):
    """
    Generate silent audio file.
    
    Args:
        output_path: Path to output WAV file
        duration_seconds: Duration in seconds
        sample_rate: Sample rate in Hz
    """
    num_samples = int(duration_seconds * sample_rate)
    
    with wave.open(output_path, 'w') as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        
        # Write silent frames (all zeros)
        silent_data = struct.pack('<' + 'h' * num_samples, *[0] * num_samples)
        wav.writeframes(silent_data)
    
    print(f"Generated silent audio: {output_path}")


def generate_tone_audio(output_path: str, duration_seconds: float, frequency: float = 440.0, sample_rate: int = 16000):
    """
    Generate audio file with a simple sine wave tone.
    
    Args:
        output_path: Path to output WAV file
        duration_seconds: Duration in seconds
        frequency: Tone frequency in Hz (default: 440Hz = A4)
        sample_rate: Sample rate in Hz
    """
    num_samples = int(duration_seconds * sample_rate)
    amplitude = 32767 * 0.5  # 50% of max 16-bit amplitude
    
    with wave.open(output_path, 'w') as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        
        # Generate sine wave
        samples = []
        for i in range(num_samples):
            value = amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)
            samples.append(int(value))
        
        audio_data = struct.pack('<' + 'h' * num_samples, *samples)
        wav.writeframes(audio_data)
    
    print(f"Generated tone audio: {output_path}")


def generate_corrupted_audio(output_path: str):
    """
    Generate intentionally corrupted WAV file for error testing.
    
    Args:
        output_path: Path to output WAV file
    """
    # Write invalid WAV data
    with open(output_path, 'wb') as f:
        f.write(b'RIFF')
        f.write(struct.pack('<I', 1000))  # File size
        f.write(b'WAVE')
        f.write(b'INVALID_CHUNK')  # Invalid chunk header
        f.write(b'\x00' * 100)  # Garbage data
    
    print(f"Generated corrupted audio: {output_path}")


def generate_test_audio_with_tts(output_path: str, text: str, duration_seconds: float = None):
    """
    Generate test audio using text-to-speech (requires pyttsx3).
    
    Args:
        output_path: Path to output WAV file
        text: Text to synthesize
        duration_seconds: Optional target duration (will pad with silence if needed)
    """
    try:
        import pyttsx3
    except ImportError:
        print("Warning: pyttsx3 not installed. Install with: pip install pyttsx3")
        print("Falling back to tone generation for:", output_path)
        generate_tone_audio(output_path, duration_seconds or 10.0)
        return
    
    # Initialize TTS engine
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Speech rate
    
    # Save to file
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    
    print(f"Generated TTS audio: {output_path}")


def main():
    """Generate all test audio fixtures."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "audio"
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating test audio fixtures...")
    print(f"Output directory: {fixtures_dir}")
    
    # Single speaker audio (10 seconds)
    single_speaker_path = fixtures_dir / "single_speaker_10s.wav"
    single_speaker_text = (
        "This is a test recording with a single speaker. "
        "The quick brown fox jumps over the lazy dog. "
        "Testing one two three."
    )
    generate_test_audio_with_tts(str(single_speaker_path), single_speaker_text, 10.0)
    
    # Multi-speaker audio (30 seconds) - Note: TTS can't do multiple voices, use tone instead
    multi_speaker_path = fixtures_dir / "multi_speaker_30s.wav"
    print(f"Note: Multi-speaker audio requires manual recording. Creating placeholder tone at {multi_speaker_path}")
    generate_tone_audio(str(multi_speaker_path), 30.0, frequency=880.0)
    
    # Corrupted audio
    corrupted_path = fixtures_dir / "corrupted.wav"
    generate_corrupted_audio(str(corrupted_path))
    
    # Silent audio (edge case)
    silent_path = fixtures_dir / "silent_5s.wav"
    generate_silent_audio(str(silent_path), 5.0)
    
    print("\nTest audio generation complete!")
    print("\nNOTE: For realistic multi-speaker testing, manually record audio with multiple speakers")
    print("and save as 'multi_speaker_30s.wav' in the fixtures directory.")


if __name__ == "__main__":
    main()
