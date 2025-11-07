"""
Async processing infrastructure for transcription operations.

Provides thread pool execution for long-running WhisperX transcription
tasks while maintaining responsiveness in the Discord bot.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, Future
from contextlib import asynccontextmanager
from typing import Any, Callable, Optional, TypeVar

T = TypeVar('T')


class AsyncProcessor:
    """
    Asynchronous processor for transcription operations.

    Manages a thread pool executor to run blocking WhisperX operations
    asynchronously, preventing the Discord bot from becoming unresponsive.
    """

    def __init__(self, max_workers: int = 8):
        """
        Initialize the async processor.

        Args:
            max_workers: Maximum number of worker threads (default: 8)
        """
        self.max_workers = max_workers
        self.executor: Optional[ThreadPoolExecutor] = None
        self.logger = logging.getLogger(self.__class__.__name__)

    async def __aenter__(self):
        """Async context manager entry."""
        self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()

    def start(self) -> None:
        """Start the thread pool executor."""
        if self.executor is None:
            self.executor = ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="transcription")
            self.logger.info(f"Started async processor with {self.max_workers} worker threads")

    async def stop(self) -> None:
        """Stop the thread pool executor."""
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None
            self.logger.info("Stopped async processor")

    async def run_in_thread(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Run a blocking function in a thread pool.

        Args:
            func: The blocking function to run
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            The result of the function call

        Raises:
            RuntimeError: If executor is not started
        """
        if not self.executor:
            raise RuntimeError("Async processor not started. Use start() or async context manager.")

        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(self.executor, func, *args, **kwargs)
            return result
        except Exception as e:
            self.logger.error(f"Error running {func.__name__} in thread: {e}")
            raise

    async def run_transcription_task(self, transcription_func: Callable[..., T],
                                   *args, **kwargs) -> T:
        """
        Run a transcription-specific task in the thread pool.

        This is a convenience method for transcription operations with
        standardized error handling and logging.

        Args:
            transcription_func: The transcription function to run
            *args: Arguments for the transcription function
            **kwargs: Keyword arguments for the transcription function

        Returns:
            Transcription result
        """
        self.logger.info(f"Starting transcription task: {transcription_func.__name__}")

        try:
            result = await self.run_in_thread(transcription_func, *args, **kwargs)
            self.logger.info(f"Completed transcription task: {transcription_func.__name__}")
            return result
        except Exception as e:
            self.logger.error(f"Transcription task failed: {transcription_func.__name__} - {e}")
            raise

    @asynccontextmanager
    async def transcription_context(self):
        """
        Context manager for transcription operations.

        Ensures proper setup and cleanup for transcription tasks.
        """
        async with self:
            try:
                yield
            except Exception as e:
                self.logger.error(f"Error in transcription context: {e}")
                raise


# Global async processor instance
_async_processor: Optional[AsyncProcessor] = None


def get_async_processor() -> AsyncProcessor:
    """Get the global async processor instance."""
    global _async_processor
    if _async_processor is None:
        _async_processor = AsyncProcessor()
    return _async_processor


async def run_transcription_async(func: Callable[..., T], *args, **kwargs) -> T:
    """
    Convenience function to run transcription tasks asynchronously.

    Uses the global async processor instance.

    Args:
        func: Transcription function to run
        *args: Arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Function result
    """
    processor = get_async_processor()
    return await processor.run_transcription_task(func, *args, **kwargs)