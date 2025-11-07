# Quickstart: audio_capture

## Prerequisites
- Python 3.7+
- Discord bot token and permissions to join/record in target voice channel
- Required dependencies installed (`pip install -r requirements.txt`)

## Steps
1. Start the bot and connect to a Discord voice channel
2. Use the `/start-recording` command to begin session
3. Speak in the voice channel; bot records all user audio
4. Use `/stop-recording` to end session
5. Find `session_audio_16k.wav` and `metadata.json` in the output directory
6. Verify audio file is mono, 16kHz, 16-bit PCM and metadata lists correct session details

## Validation
- Play the audio file to confirm quality and format
- Inspect metadata.json for completeness and accuracy
- Run `pytest` to validate automated tests
- Update documentation as needed
