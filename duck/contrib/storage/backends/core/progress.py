"""
Progress reporting module for storage backends.
"""

import math
import inspect

from typing import Callable
from dataclasses import dataclass


DEFAULT_PROGRESS_STEP = 5.0

# Typing
ProgressCallback = Callable[["ProgressEvent"], None]


@dataclass(frozen=True)
class ProgressEvent:
    """
    A progress report for an upload in flight.

    Attributes:
        key: Storage key the file is being written to.
        filename: Sanitized filename of the upload.
        sent: Bytes handed to the backend so far.
        total: Total size of the payload in bytes.
        percent: Completion percentage from 0.0 to 100.0.
    """

    key: str
    filename: str
    sent: int
    total: int
    percent: float


class ProgressReporter:
    """
    Converts byte counts into progress events for registered callbacks.

    Emits an event at 0%, each time the percentage passes another step
    increment, and once at 100%. Callbacks may be plain functions or
    coroutine functions; the async methods await the latter.
    """

    def __init__(
        self,
        total: int,
        step: float,
        callbacks: list[ProgressCallback],
        key: str,
        filename: str,
    ) -> None:
        """
        Initializes the reporter.

        Args:
            total: Total payload size in bytes.
            step: Percentage increment between events, such as 5.0.
            callbacks: Functions that receive each ProgressEvent.
            key: Storage key the file is written to.
            filename: Sanitized filename of the upload.
        """
        self.total = total
        self.step = step
        self.callbacks = callbacks
        self.key = key
        self.filename = filename
        self.sent = 0
        self.next_mark = step
        self.last_percent: float | None = None

    def percent(self) -> float:
        """
        Computes the current completion percentage.

        Returns:
            The percentage of bytes sent, from 0.0 to 100.0.
        """
        if self.total == 0:
            return 100.0
        return min(100.0, self.sent * 100 / self.total)

    def build_event(self, percent: float) -> ProgressEvent:
        """
        Creates the event describing the current state.

        Args:
            percent: Completion percentage to report.

        Returns:
            A ProgressEvent for the current state.
        """
        self.last_percent = percent

        return ProgressEvent(
            key=self.key,
            filename=self.filename,
            sent=self.sent,
            total=self.total,
            percent=percent,
        )

    def record(self, size: int) -> float | None:
        """
        Adds sent bytes and returns the percentage when a step boundary is crossed.

        Args:
            size: Number of bytes just handed to the transport.

        Returns:
            The percentage to report, or None if no event is due.
        """
        self.sent = min(self.sent + size, self.total)
        percent = self.percent()

        if self.next_mark <= percent < 100:
            self.next_mark = (math.floor(percent / self.step) + 1) * self.step
            return percent

        return None

    def complete(self) -> bool:
        """
        Marks the upload as finished if the 100% event has not been sent yet.

        Returns:
            True if the 100% event should be emitted, otherwise False.
        """
        if self.last_percent == 100.0:
            return False

        # Set sent data
        self.sent = self.total

        # Return final flag
        return True

    def emit(self, percent: float) -> None:
        """
        Sends one event to every callback.

        Args:
            percent: Completion percentage to report.
        """
        event = self.build_event(percent)

        for callback in self.callbacks:
            callback(event)

    async def async_emit(self, percent: float) -> None:
        """
        Sends one event to every callback, awaiting coroutine callbacks.

        Args:
            percent: Completion percentage to report.
        """
        event = self.build_event(percent)

        for callback in self.callbacks:
            result = callback(event)

            if inspect.isawaitable(result):
                # Callback is an async callback so await it
                await result # type: ignore

    def start(self) -> None:
        """
        Emits the 0% event before any bytes are sent.
        """
        self.emit(0.0)

    async def async_start(self) -> None:
        """
        Async version of ``start``.
        """
        await self.async_emit(0.0)

    def advance(self, size: int) -> None:
        """
        Records bytes sent and emits an event when a step boundary is crossed.

        Args:
            size: Number of bytes just handed to the transport.
        """
        percent = self.record(size)

        if percent is not None:
            self.emit(percent)

    async def async_advance(self, size: int) -> None:
        """
        Async version of ``advance``.

        Args:
            size: Number of bytes just handed to the transport.
        """
        percent = self.record(size)

        if percent is not None:
            await self.async_emit(percent)

    def finish(self) -> None:
        """
        Emits the 100% event once the upload has completed.
        """
        if self.complete():
            self.emit(100.0)

    async def async_finish(self) -> None:
        """
        Async version of ``finish``.
        """
        if self.complete():
            await self.async_emit(100.0)
