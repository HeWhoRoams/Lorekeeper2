import io
import wave
from typing import Tuple

import speech_recognition as sr

def convert_audio_to_wav(audio_data: sr.AudioData) -> bytes:
    """
    Convert speech recognition AudioData to 16kHz mono 16-bit PCM WAV bytes.
    """
    # Convert to WAV data
    wav_data = audio_data.get_wav_data()

    # Load into BytesIO for processing
    wav_io = io.BytesIO(wav_data)

    # Open as WAV file to check and convert format
    with wave.open(wav_io, 'rb') as wav_file:
        # Get current parameters
        nchannels, sampwidth, framerate, nframes, comptype, compname = wav_file.getparams()

        # If already 16kHz mono 16-bit, return as is
        if framerate == 16000 and nchannels == 1 and sampwidth == 2:
            return wav_data

        # Read frames
        frames = wav_file.readframes(nframes)

    # Create new WAV with desired format
    output_io = io.BytesIO()
    with wave.open(output_io, 'wb') as out_wav:
        out_wav.setnchannels(1)  # Mono
        out_wav.setsampwidth(2)  # 16-bit
        out_wav.setframerate(16000)  # 16kHz
        out_wav.writeframes(frames)

    return output_io.getvalue()

def save_wav_file(wav_bytes: bytes, file_path: str) -> None:
    """
    Save WAV bytes to file.
    """
    with open(file_path, 'wb') as f:
        f.write(wav_bytes)

def get_audio_duration(wav_bytes: bytes) -> float:
    """
    Get duration of WAV audio in seconds.
    """
    wav_io = io.BytesIO(wav_bytes)
    with wave.open(wav_io, 'rb') as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        return frames / float(rate)