import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import List, Optional

import discord
import speech_recognition as sr

from src.models.session_audio import SessionAudio
from src.models.session_metadata import SessionMetadata
from src.utils.audio_utils import convert_audio_to_wav, get_audio_duration, save_wav_file

logger = logging.getLogger(__name__)

class SessionRecorder:
    def __init__(self, voice_client: discord.VoiceClient, guild_id: str, channel_id: str):
        self.voice_client = voice_client
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.participants: List[str] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.audio_data: List[sr.AudioData] = []
        self.is_recording = False

    def start_recording(self) -> None:
        """Start recording the session."""
        if self.is_recording:
            logger.warning("Recording already in progress")
            return

        self.start_time = time.time()
        self.participants = [str(member.id) for member in self.voice_client.channel.members if not member.bot]
        self.audio_data = []
        self.is_recording = True
        logger.info(f"Started recording session in guild {self.guild_id}, channel {self.channel_id}")

    def stop_recording(self) -> Tuple[Optional[SessionAudio], Optional[SessionMetadata]]:
        """Stop recording and return session data."""
        if not self.is_recording:
            logger.warning("No recording in progress")
            return None, None

        self.end_time = time.time()
        self.is_recording = False

        if not self.audio_data:
            logger.error("No audio data recorded")
            return None, None

        # Combine audio data
        combined = sr.AudioData(
            b''.join(data.get_raw_data() for data in self.audio_data),
            self.audio_data[0].sample_rate,
            self.audio_data[0].sample_width
        )

        # Convert to WAV
        try:
            wav_bytes = convert_audio_to_wav(combined)
            duration = get_audio_duration(wav_bytes)

            # Create output directory
            output_dir = f".logs/audio_sessions/{self.guild_id}"
            os.makedirs(output_dir, exist_ok=True)

            # Save audio file
            timestamp = datetime.fromtimestamp(self.start_time).strftime('%Y%m%d_%H%M%S')
            audio_file_path = f"{output_dir}/session_{timestamp}.wav"
            save_wav_file(wav_bytes, audio_file_path)

            # Create metadata
            metadata = SessionMetadata(
                guild_id=self.guild_id,
                channel_id=self.channel_id,
                participants=self.participants,
                start_time=datetime.fromtimestamp(self.start_time).isoformat(),
                end_time=datetime.fromtimestamp(self.end_time).isoformat(),
                duration=duration,
                file_path=audio_file_path
            )

            # Save metadata
            metadata_file_path = f"{output_dir}/session_{timestamp}_metadata.json"
            with open(metadata_file_path, 'w') as f:
                json.dump({
                    "guild_id": metadata.guild_id,
                    "channel_id": metadata.channel_id,
                    "participants": metadata.participants,
                    "start_time": metadata.start_time,
                    "end_time": metadata.end_time,
                    "duration": metadata.duration,
                    "file_path": metadata.file_path
                }, f, indent=2)

            session_audio = SessionAudio(
                file_path=audio_file_path,
                duration=duration
            )

            logger.info(f"Session recorded: {audio_file_path}, duration: {duration:.2f}s")
            return session_audio, metadata

        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return None, None

    def add_audio_data(self, data: sr.AudioData) -> None:
        """Add audio data from the voice channel."""
        if self.is_recording:
            self.audio_data.append(data)