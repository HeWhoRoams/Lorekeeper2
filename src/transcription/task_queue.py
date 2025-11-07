"""
Async Transcription Task Queue
Queues transcription jobs for background processing
"""
import asyncio
from typing import Any, Dict

class TranscriptionTaskQueue:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def add_task(self, task: Dict[str, Any]):
        await self.queue.put(task)

    async def get_task(self) -> Dict[str, Any]:
        return await self.queue.get()

    def task_done(self):
        self.queue.task_done()
