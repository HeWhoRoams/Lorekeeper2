"""
Async Transcription Job Manager
Handles background transcription jobs for Discord bot
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, Any

class TranscriptionJobManager:
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.loop = asyncio.get_event_loop()
        self.jobs: Dict[str, asyncio.Future] = {}

    def submit_job(self, job_id: str, func: Callable, *args, **kwargs) -> asyncio.Future:
        future = self.loop.run_in_executor(self.executor, func, *args, **kwargs)
        self.jobs[job_id] = future
        return future

    def get_job_status(self, job_id: str) -> str:
        future = self.jobs.get(job_id)
        if not future:
            return "not_found"
        if future.done():
            if future.exception():
                return "failed"
            return "completed"
        return "running"

    def cleanup_job(self, job_id: str):
        if job_id in self.jobs:
            del self.jobs[job_id]
