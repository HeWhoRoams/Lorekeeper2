import asyncio
import logging
import os
import time
from datetime import datetime

import discord
import yaml
from dotenv import load_dotenv

from src.bot.helper import BotHelper
from src.config.cliargs import CLIArgs
from src.utils.commandline import CommandLine
from src.utils.pdf_generator import pdf_generator
from src.utils.session_recorder import SessionRecorder
from src.sinks.recording_sink import RecordingSink
# US3: Async transcription imports
from src.transcription.job_manager import TranscriptionJobManager
from src.transcription.task_queue import TranscriptionTaskQueue
from src.transcription.transcription_service import TranscriptionService

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PLAYER_MAP_FILE_PATH = os.getenv("PLAYER_MAP_FILE_PATH")

logger = logging.getLogger()  # root logger


def configure_logging():
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('faster_whisper').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)

    # Ensure the directory exists
    log_directory = '.logs/transcripts'
    pdf_directory = '.logs/pdfs'
    os.makedirs(log_directory, exist_ok=True) 
    os.makedirs(pdf_directory, exist_ok=True)  

    # Get the current date for the log file name
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_filename = os.path.join(log_directory, f"{current_date}-transcription.log")

    # Custom logging format (date with milliseconds, message)
    log_format = '%(asctime)s %(name)s: %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S.%f'[:-3]  # Trim to milliseconds

    if CLIArgs.verbose:
        logger.setLevel(logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG,
                            format=log_format,
                            datefmt=date_format)
    else:
        logger.setLevel(logging.INFO)
        logging.basicConfig(level=logging.INFO,
                            format=log_format,
                            datefmt=date_format)
    
    # Set up the transcription logger
    transcription_logger = logging.getLogger('transcription')
    transcription_logger.setLevel(logging.INFO)

    # File handler for transcription logs (append mode)
    file_handler = logging.FileHandler(log_filename, mode='a')
    file_handler.setLevel(logging.INFO)
    
    # Custom formatter WITHOUT the automatic timestamp
    file_handler.setFormatter(logging.Formatter(
        '%(message)s'  # Only log the custom message, no automatic timestamp
    ))

    # Add the handler to the transcription logger
    transcription_logger.addHandler(file_handler)


if __name__ == "__main__":
    args = CommandLine.read_command_line()
    CLIArgs.update_from_args(args)

    configure_logging()
    loop = asyncio.get_event_loop()

    from src.bot.volo_bot import VoloBot
    bot = VoloBot(loop)

    # US3: Async transcription job manager and queue
    job_manager = TranscriptionJobManager(max_workers=4)
    task_queue = TranscriptionTaskQueue()
    transcription_service = TranscriptionService()

    @bot.slash_command(name="transcribe_async", description="Run transcription in the background (async)")
    async def transcribe_async(ctx: discord.context.ApplicationContext):
        guild_id = ctx.guild_id
        helper = bot.guild_to_helper.get(guild_id, None)
        if not helper:
            await ctx.respond("Not connected to a voice channel.", ephemeral=True)
            return
        # Assume session_audio_16k.wav and metadata.json are saved in a known location
        audio_path = f"Sessions/{guild_id}/session_audio_16k.wav"
        metadata_path = f"Sessions/{guild_id}/metadata.json"
        job_id = f"transcribe_{guild_id}_{int(time.time())}"

        async def run_transcription_job():
            result = await transcription_service.transcribe_audio(Path(audio_path), Path(metadata_path))
            # Notify user when done
            channel = ctx.channel
            if result.get("error"):
                await channel.send(f"❌ Transcription failed: {result['error']}")
            else:
                await channel.send(f"✅ Transcription complete! Transcript: {result['transcript_path']}")

        # Submit job to job manager
        future = job_manager.submit_job(job_id, lambda: asyncio.run(run_transcription_job()))
        await ctx.respond(f"Transcription started in background. Job ID: {job_id}", ephemeral=True)

    @bot.slash_command(name="transcription_status", description="Check status of async transcription job")
    async def transcription_status(ctx: discord.context.ApplicationContext, job_id: str):
        status = job_manager.get_job_status(job_id)
        await ctx.respond(f"Transcription job {job_id} status: {status}", ephemeral=True)

    @bot.slash_command(name="notify_on_completion", description="Get notified when transcription finishes")
    async def notify_on_completion(ctx: discord.context.ApplicationContext, job_id: str):
        future = job_manager.jobs.get(job_id)
        if not future:
            await ctx.respond(f"No such job: {job_id}", ephemeral=True)
            return
        while not future.done():
            await asyncio.sleep(2)
        if future.exception():
            await ctx.respond(f"❌ Transcription job {job_id} failed: {future.exception()}", ephemeral=True)
        else:
            await ctx.respond(f"✅ Transcription job {job_id} completed!", ephemeral=True)

    # ...existing code...

    @bot.slash_command(name="transcribe_now", description="Run transcription immediately (sync)")
    async def transcribe_now(ctx: discord.context.ApplicationContext):
        guild_id = ctx.guild_id
        helper = bot.guild_to_helper.get(guild_id, None)
        if not helper:
            await ctx.respond("Not connected to a voice channel.", ephemeral=True)
            return
        audio_path = f"Sessions/{guild_id}/session_audio_16k.wav"
        metadata_path = f"Sessions/{guild_id}/metadata.json"
        await ctx.trigger_typing()
        result = await transcription_service.transcribe_audio(Path(audio_path), Path(metadata_path))
        if result.get("error"):
            await ctx.respond(f"❌ Transcription failed: {result['error']}", ephemeral=True)
        else:
            await ctx.respond(f"✅ Transcription complete! Transcript: {result['transcript_path']}", ephemeral=False)