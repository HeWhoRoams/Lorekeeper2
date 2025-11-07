import logging
from typing import Optional

import speech_recognition as sr
from discord.sinks.core import Filters, Sink, default_filters

from src.sinks.session_recorder import SessionRecorder

logger = logging.getLogger(__name__)

class RecordingSink(Sink):
    """A sink for recording Discord voice channel audio."""

    def __init__(self, recorder: SessionRecorder, *, filters=None):
        self.recorder = recorder
        if filters is None:
            filters = default_filters
        self.filters = filters
        Filters.__init__(self, **self.filters)

    @Filters.container
    def write(self, data, user):
        """Receive audio data from Discord."""
        if self.recorder.is_recording:
            # Convert Discord audio data to speech_recognition AudioData
            # Discord provides PCM data at 48kHz stereo 16-bit
            audio_data = sr.AudioData(data, 48000, 4)  # 48kHz, 16-bit stereo = 4 bytes per sample
            self.recorder.add_audio_data(audio_data)