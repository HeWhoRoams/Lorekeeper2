# V.O.L.O Discord Transcription Bot

This project is a Discord bot that transcribes voice channel audio into text in real-time. It uses Whisper for audio transcription and is capable of handling multiple users in a voice channel.

## Features

- This project uses Pycord (see [Pycord Github](https://github.com/Pycord-Development/pycord))
- This project uses Faster Whisper (see [Faster Whisper Github](https://github.com/SYSTRAN/faster-whisper))
- **Real-time transcription**: Transcribes voice channel audio to text in real-time.
- **Session recording**: Records entire voice sessions with separate audio tracks per user.
- **Async audio transcription**: Process recorded audio files with WhisperX in the background without blocking the bot.
- **Speaker diarization**: Identifies and labels different speakers in multi-speaker audio (optional).
- **Word-level alignment**: Generates precise timestamps for each word in transcripts.
- **Multiple users support**: Handles concurrent transcriptions for multiple Discord servers.
- **Thread-safe operations**: Safe concurrent operations across guilds and voice channels.

## Setup

To set up and run this Discord bot, follow these steps:

### Prerequisites

- Python 3.7 or higher.
- Discord bot token (see [Discord Developer Portal](https://discord.com/developers/applications)).
- `ffmpeg` installed and added to your system's PATH.

### Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-github-username/discord-transcription-bot.git
   cd discord-transcription-bot
   ```

2. **Create a Virtual Environment (optional but recommended):**

   ```bash
   python -m venv venv
   # Activate the virtual environment
   # On Windows: venv\Scripts\activate
   # On macOS/Linux: source venv/bin/activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**

   Create a `.env` file in the root directory and add your Discord bot token and other configuration:

   ```
   DISCORD_BOT_TOKEN=your_discord_bot_token
   DISCORD_CHANNEL_ID=your_channel_id
   PLAYER_MAP_FILE_PATH=./player_map.yml
   TRANSCRIPTION_METHOD=local
   TRANSCRIPTION_MODEL=large-v3
   TRANSCRIPTION_DIARIZATION=false
   HF_TOKEN=your_huggingface_token_for_diarization
   ```

### Configuration

- Edit `player_map.yml` to map Discord user IDs to player and character names for transcription.
- Configure transcription settings in `.env`:
  - `TRANSCRIPTION_MODEL`: WhisperX model to use (default: `large-v3`)
  - `TRANSCRIPTION_DIARIZATION`: Enable speaker diarization (`true`/`false`)
  - `HF_TOKEN`: HuggingFace token for pyannote.audio diarization models

## Audio Transcription Workflow

### Real-Time Transcription (Legacy)
1. Connect bot to voice channel with `/connect`
2. Start transcription with `/scribe`
3. Bot transcribes audio in real-time using Whisper
4. Stop with `/stop` when done

### Session Recording + Async Transcription (Recommended)
1. Connect bot to voice channel with `/connect`
2. Start recording with `/start_recording`
3. Have your voice session
4. Stop recording with `/stop_recording` (saves `session_audio_16k.wav` and `metadata.json`)
5. Run async transcription with `/transcribe_async` (runs in background)
6. Check status with `/transcription_status <job_id>`
7. Retrieve transcript from `Sessions/<guild_id>/session_audio_16k_transcript.json`

### Transcription Output Format

Transcripts are saved as JSON with the following structure:

```json
{
  "metadata": {
    "created_at": "2025-11-07T12:00:00",
    "format_version": "1.0",
    "transcription_model": "large-v3",
    "total_segments": 42,
    "total_duration": 120.5
  },
  "segments": [
    {
      "start_time": 0.0,
      "end_time": 2.5,
      "text": "Hello, welcome to the session!",
      "speaker_label": "SPEAKER_00",
      "words": [
        {"word": "Hello", "start": 0.0, "end": 0.5, "confidence": 0.95}
      ]
    }
  ],
  "log": {
    "timestamp": "2025-11-07T12:00:00",
    "runtime_seconds": 45.2,
    "model_name": "large-v3",
    "accuracy_metrics": {"average_confidence": 0.92},
    "errors": [],
    "successful": true
  }
}
```

## Usage

1. **Start the Bot:**

   ```bash
   python main.py
   ```

2. **Bot Commands:**

   **Voice Channel Commands:**
   - `/connect`: Connect VOLO to your voice channel.
   - `/disconnect`: Disconnects the bot from the voice channel.
   
   **Real-Time Transcription:**
   - `/scribe`: Starts real-time transcription in the current voice channel.
   - `/stop`: Stops the real-time transcription.
   
   **Session Recording:**
   - `/start_recording`: Start recording the voice session.
   - `/stop_recording`: Stop recording and save the session.
   
   **Async Audio Transcription:**
   - `/transcribe_async`: Run WhisperX transcription in the background on recorded audio.
   - `/transcribe_now`: Run WhisperX transcription immediately (synchronous).
   - `/transcription_status <job_id>`: Check the status of a background transcription job.
   - `/notify_on_completion <job_id>`: Get notified when a transcription job completes.
   
   **Utilities:**
   - `/generate_pdf`: Generate a PDF of the transcriptions.
   - `/help`: Show the help message with all available commands.

## Contributing

Contributions to this project are welcome. Please ensure to follow the project's coding style and submit pull requests for any new features or bug fixes.

## License

[MIT License](LICENSE)

## Acknowledgments

- This project uses [Whisper](https://github.com/openai/whisper) for audio transcription.
- Thanks to the Discord.py community for their support and resources.
