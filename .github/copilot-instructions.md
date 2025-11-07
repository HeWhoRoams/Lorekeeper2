# V.O.L.O Discord Transcription Bot - AI Agent Guidelines

## Architecture Overview
This is a real-time Discord voice transcription bot using Whisper AI. The core architecture separates concerns:
- **VoloBot** (`src/bot/volo_bot.py`): Discord bot logic, command handling, guild state management
- **SessionRecorder** (`src/sinks/session_recorder.py`): Audio session recording and file saving
- **RecordingSink** (`src/sinks/recording_sink.py`): Discord audio capture sink
- **WhisperSink** (`src/sinks/whisper_sink.py`): Audio capture and transcription processing
- **BotHelper** (`src/bot/helper.py`): Voice client management and status updates

## Key Design Patterns

### Thread-Safe Audio Processing
- Audio transcription runs in background threads using `ThreadPoolExecutor(max_workers=8)`
- Main Discord bot loop remains responsive while processing audio
- Use `asyncio.Queue` for thread-safe communication between audio processing and Discord responses

### Guild-Based Isolation
- Each Discord server (guild) maintains separate state in dictionaries:
  - `guild_to_helper`: Voice client management per server
  - `guild_is_recording`: Recording status per server
  - `guild_whisper_sinks`: Audio processing instances per server
- Always check `ctx.guild_id` for server-specific operations

### Structured Transcription Logging
- Transcriptions stored as JSON with fields: `date`, `begin`, `end`, `user_id`, `player`, `character`, `event_source`, `data`
- Separate `transcription` logger writes to date-stamped files in `.logs/transcripts/`
- Use `json.dumps()` for serialization, `json.loads()` for parsing

### Player Mapping System
- Maps Discord user IDs to player/character names via YAML file
- Loaded at startup from `PLAYER_MAP_FILE_PATH` environment variable
- Updated dynamically via `/update_player_map` command
- Format: `{user_id: {"player": "name", "character": "character_name"}}`

## Critical Workflows

### Bot Startup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.sample .env
# Edit .env with DISCORD_BOT_TOKEN and other settings

# 3. Configure player mapping
cp player_map.yml.sample player_map.yml
# Edit with Discord user IDs and character names

# 4. Start bot
python main.py [--verbose]
```

### Audio Processing Pipeline
1. `/connect` → Join voice channel, create BotHelper and voice client
2. `/start_recording` → Start SessionRecorder with RecordingSink, begin audio capture
3. Audio flows: Discord → RecordingSink → SessionRecorder → audio_data list
4. `/stop_recording` → Stop recording, convert audio to WAV, save files and metadata
5. `/disconnect` → Cleanup voice client and recorders

### Transcription Flow
- Audio captured in 50ms chunks via `Sink.write()` method
- Speaker detection groups audio by user ID
- Transcription triggered after 1.5s silence
- Results queued for Discord output and file logging

## Environment Configuration
```bash
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_CHANNEL_ID=channel_id
PLAYER_MAP_FILE_PATH=./player_map.yml
TRANSCRIPTION_METHOD=local  # or "openai"
```

## Development Conventions

### Logging Setup
- Root logger configured in `main.py::configure_logging()`
- Separate transcription logger for structured JSON output
- Suppress noisy libraries (discord, asyncio, faster_whisper, httpx)
- Log levels: DEBUG (verbose), INFO (normal), WARNING/ERROR (issues)

### Error Handling
- Audio processing failures retry after 5 seconds
- Voice client disconnections trigger cleanup
- Thread exceptions logged but don't crash main bot
- Use try/catch blocks around transcription calls

### Async/Await Patterns
- Discord commands are async (`async def command_name(ctx)`)
- Use `await ctx.trigger_typing()` for long operations
- Voice operations are synchronous but wrapped in async context
- Queue operations use `await queue.get()` for async consumption

## Common Pitfalls

### Audio Processing
- Whisper requires minimum 0.1s audio length for transcription
- GPU memory check: fallback to CPU if <5GB VRAM
- VAD (Voice Activity Detection) filters silence with `min_silence_duration_ms=150`

### Discord Integration
- Bot status changes via `guild.get_member(bot.user.id).edit(nick=name)`
- Voice state updates handled in `on_voice_state_update` event
- Commands check voice channel presence before operations

### State Management
- Always cleanup sinks and tasks on disconnect
- Use guild IDs as keys for all server-specific state
- Clear references to prevent memory leaks

## Testing Approach
- Manual testing required for audio features (Discord voice channels)
- Use `/help` command to verify bot responsiveness
- Check `.logs/transcripts/` for transcription output
- PDF generation testable via `/generate_pdf` after recording

## File Organization
- `main.py`: Entry point, command definitions, logging setup
- `src/bot/`: Core bot logic and helpers
- `src/sinks/`: Audio processing components (recording and transcription)
- `src/config/`: Configuration classes
- `src/utils/`: PDF generation, CLI parsing, audio/metadata utilities
- `src/models/`: Data models for sessions
- `assets/`: Static files (background images)
- `.logs/`: Runtime logs and generated audio/PDFs

### II. Session-End Audio Transcription
The bot MUST reliably join Discord voice channels, record session audio, and transcribe only after the session ends.
Audio MUST be saved during the session and processed in batch at completion, not in real time.
Transcription MUST support multiple speakers and log results in structured, queryable formats.
Rationale: Ensures accurate, multi-user transcription for session archiving and review, while reducing real-time resource requirements.