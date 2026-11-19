"""
A reusable memory inspection and profiling utility for Python applications.

Features:
    - Python allocation tracking through tracemalloc.
    - Before/after allocation snapshots.
    - Peak traced memory reporting.
    - Optional process RSS inspection.
    - Optional garbage collection before profiling.
    - Allocation statistics by source location.
    - Execution duration measurement.
    - Console and logger output.
    - Custom reporting callbacks.
    - Synchronous and asynchronous function support.
    - Direct invocation and decorator usage.

Usage:
    ```python
    # Direct invocation
    MemoryProfiler.track_memory(my_function)

    # Direct invocation with function arguments
    MemoryProfiler.track_memory(
        my_function,
        args=(100, "value"),
        kwargs={"enabled": True},
        top=20,
    )

    # Decorator
    @MemoryProfiler.track_memory(log_to_console=True, top=15)
    def my_function():
        ...

    # Async decorator
    @MemoryProfiler.track_memory(log_to_console=True)
    async def my_async_function():
        ...

    # Collect reports programmatically
    reports = []

    MemoryProfiler.track_memory(
        my_function,
        callback=reports.append,
        log_to_console=False,
    )
    ```

Notes:
    tracemalloc is process-global. This module never stops a tracing
    session started by another component.

    Memory reports represent process-wide measurements. Concurrent
    profiling operations should not be interpreted as isolated results.

    RSS measures resident process memory, while tracemalloc measures Python
    allocations. They describe different aspects of memory usage.
"""

from __future__ import annotations

import functools
import gc
import inspect
import logging
import os
import time
import tracemalloc
import warnings

from dataclasses import dataclass, field
from typing import Any, Callable


__all__ = [
    "MemoryReport",
    "MemoryProfiler",
]


@dataclass
class MemoryReport:
    """
    Contains the results of a memory profiling operation.

    Attributes:
        function: Name of the profiled function.
        duration: Execution duration in seconds.
        current_before: Current traced memory before execution.
        current_after: Current traced memory after execution.
        current_diff: Difference in traced memory.
        peak_before: Traced memory peak before execution.
        peak_after: Traced memory peak after execution.
        rss_before: Process RSS before execution.
        rss_after: Process RSS after execution.
        rss_diff: Difference in process RSS.
        allocations: Top allocation differences between snapshots.
        error: Exception raised by the profiled function, if any.
    """

    function: str
    duration: float = 0.0
    current_before: int = 0
    current_after: int = 0
    current_diff: int = 0
    peak_before: int = 0
    peak_after: int = 0
    rss_before: int | None = None
    rss_after: int | None = None
    rss_diff: int | None = None
    allocations: list[str] = field(default_factory=list)
    error: str | None = None

    @staticmethod
    def format_size(size: int | None) -> str:
        """
        Convert bytes into a human-readable memory size.

        Args:
            size: Memory size in bytes.

        Returns:
            Formatted memory size.
        """
        if size is None:
            return "N/A"

        value = float(size)

        for unit in ("B", "KB", "MB", "GB", "TB"):
            if abs(value) < 1024 or unit == "TB":
                return f"{value:.2f} {unit}"

            value /= 1024

        return f"{value:.2f} TB"

    def summary(self) -> dict[str, Any]:
        """
        Return a machine-readable representation of the report.

        Returns:
            Dictionary containing profiling statistics.
        """
        return {
            "function": self.function,
            "duration": self.duration,
            "current_before": self.current_before,
            "current_after": self.current_after,
            "current_diff": self.current_diff,
            "peak_before": self.peak_before,
            "peak_after": self.peak_after,
            "rss_before": self.rss_before,
            "rss_after": self.rss_after,
            "rss_diff": self.rss_diff,
            "allocations": list(self.allocations),
            "error": self.error,
        }

    def __str__(self) -> str:
        """
        Format the profiling report for console output.

        Returns:
            Human-readable profiling report.
        """
        lines = [
            "",
            "=" * 68,
            f" MEMORY REPORT: {self.function}",
            "=" * 68,
            f" Execution time:  {self.duration:.6f} seconds",
            "",
            " Python allocations:",
            f"   Before:        {self.format_size(self.current_before)}",
            f"   After:         {self.format_size(self.current_after)}",
            f"   Difference:    {self.format_size(self.current_diff)}",
            f"   Peak before:   {self.format_size(self.peak_before)}",
            f"   Peak after:    {self.format_size(self.peak_after)}",
        ]

        if self.rss_before is not None:
            lines.extend([
                "",
                " Process memory (RSS):",
                f"   Before:        {self.format_size(self.rss_before)}",
                f"   After:         {self.format_size(self.rss_after)}",
                f"   Difference:    {self.format_size(self.rss_diff)}",
            ])

        if self.allocations:
            lines.extend([
                "",
                " Top memory allocation differences:",
            ])

            lines.extend(
                f"   {allocation}"
                for allocation in self.allocations
            )

        if self.error:
            lines.extend([
                "",
                f" Exception: {self.error}",
            ])

        lines.extend([
            "=" * 68,
            "",
        ])

        return "\n".join(lines)


class MemoryProfiler:
    """
    A utility class for profiling memory usage of functions.

    This class provides methods to profile both synchronous and asynchronous
    functions, capturing memory statistics before and after execution.
    """

    @staticmethod
    def get_rss() -> int | None:
        """
        Get the current process resident memory size.

        Uses psutil when available, falling back to Linux /proc.

        Returns:
            Current RSS in bytes, or None if unavailable.
        """
        try:
            import psutil

            return psutil.Process(os.getpid()).memory_info().rss

        except Exception:
            # psutil is optional. Continue with the platform fallback.
            pass

        try:
            with open("/proc/self/statm", encoding="utf-8") as file:
                resident_pages = int(file.read().split()[1])

            return resident_pages * os.sysconf("SC_PAGE_SIZE")

        except (OSError, ValueError, IndexError, AttributeError):
            return None

    @staticmethod
    def collect_allocations(
        before: tracemalloc.Snapshot,
        after: tracemalloc.Snapshot,
        top: int,
        compare_by: str,
    ) -> list[str]:
        """
        Compare snapshots and return allocation differences.

        Args:
            before: Initial memory snapshot.
            after: Final memory snapshot.
            top: Maximum number of entries to return.
            compare_by: Grouping strategy.

        Returns:
            Formatted allocation statistics.
        """
        stats = after.compare_to(before, compare_by)

        return [
            str(stat)
            for stat in stats[:top]
        ]

    @staticmethod
    def build_report(
        *,
        function: str,
        started: float,
        current_before: int,
        peak_before: int,
        rss_before: int | None,
        before: tracemalloc.Snapshot | None,
        top: int,
        compare_by: str,
        include_rss: bool,
        error: BaseException | None = None,
    ) -> MemoryReport:
        """
        Build a profiling report from the current process state.

        Args:
            function: Profiled function name.
            started: Execution start time from perf_counter.
            current_before: Initial traced memory.
            peak_before: Initial traced memory peak.
            rss_before: Initial RSS, when enabled.
            before: Initial allocation snapshot.
            top: Number of allocation differences to include.
            compare_by: Snapshot grouping strategy.
            include_rss: Whether to collect final RSS.
            error: Exception raised during execution, if any.

        Returns:
            Completed memory report.
        """
        current_after, peak_after = tracemalloc.get_traced_memory()
        rss_after = MemoryProfiler.get_rss() if include_rss else None

        # Capture the final allocation snapshot if requested.
        after = (
            tracemalloc.take_snapshot()
            if before is not None
            else None
        )

        # Compare snapshots to collect allocation differences.
        allocations = (
            MemoryProfiler.collect_allocations(
                before,
                after,
                top,
                compare_by,
            )
            if before is not None and after is not None
            else []
        )

        # Build and return the memory report.
        return MemoryReport(
            function=function,
            duration=time.perf_counter() - started,
            current_before=current_before,
            current_after=current_after,
            current_diff=current_after - current_before,
            peak_before=peak_before,
            peak_after=peak_after,
            rss_before=rss_before,
            rss_after=rss_after,
            rss_diff=(
                rss_after - rss_before
                if rss_before is not None and rss_after is not None
                else None
            ),
            allocations=allocations,
            error=(
                f"{type(error).__name__}: {error}"
                if error is not None
                else None
            ),
        )

    @staticmethod
    def emit_report(
        report: MemoryReport,
        *,
        log_to_console: bool,
        logger: logging.Logger | None,
        callback: Callable[[MemoryReport], Any] | None,
    ) -> None:
        """
        Deliver a completed report to configured output destinations.

        Args:
            report: Completed profiling report.
            log_to_console: Whether to print the report.
            logger: Optional Python logger.
            callback: Optional synchronous report callback.
        """
        if log_to_console:
            print(report)

        if logger is not None:
            logger.info("%s", report)

        if callback is not None:
            callback(report)

    @staticmethod
    def prepare_profile(
        *,
        collect_garbage: bool,
        compare_allocations: bool,
        include_rss: bool,
    ) -> tuple[
        int,
        int,
        int | None,
        tracemalloc.Snapshot | None,
    ]:
        """
        Capture initial measurements after tracing has been enabled.

        Args:
            collect_garbage: Whether to collect unreachable objects first.
            compare_allocations: Whether to capture an initial snapshot.
            include_rss: Whether to capture initial process RSS.

        Returns:
            Tuple containing initial traced memory, peak, RSS, and snapshot.
        """
        if collect_garbage:
            gc.collect()

        # Capture the initial snapshot before reading the baseline so that
        # the snapshot's own allocations are part of the baseline.
        before = (
            tracemalloc.take_snapshot()
            if compare_allocations
            else None
        )

        current_before, peak_before = tracemalloc.get_traced_memory()
        rss_before = MemoryProfiler.get_rss() if include_rss else None

        return (
            current_before,
            peak_before,
            rss_before,
            before,
        )

    @staticmethod
    def _emit_safely(
        report: MemoryReport,
        *,
        log_to_console: bool,
        logger: logging.Logger | None,
        callback: Callable[[MemoryReport], Any] | None,
    ) -> None:
        """
        Emit a report without masking an exception from the target function.

        Reporting is secondary to the operation being profiled. Failures in
        printing, logging, or callbacks are surfaced as runtime warnings.

        Args:
            report: Completed profiling report.
            log_to_console: Whether to print the report.
            logger: Optional Python logger.
            callback: Optional synchronous report callback.
        """
        try:
            MemoryProfiler.emit_report(
                report,
                log_to_console=log_to_console,
                logger=logger,
                callback=callback,
            )
        except Exception as exc:
            warnings.warn(
                f"Memory profiling report delivery failed: {exc}",
                RuntimeWarning,
                stacklevel=2,
            )

    @staticmethod
    def _profile(
        func: Callable,
        args: tuple,
        kwargs: dict,
        *,
        log_to_console: bool,
        top: int,
        trace_depth: int,
        collect_garbage: bool,
        include_rss: bool,
        compare_allocations: bool,
        logger: logging.Logger | None,
        callback: Callable[[MemoryReport], Any] | None,
        compare_by: str,
    ) -> Any:
        """
        Execute a synchronous function and collect memory statistics.

        Returns:
            The profiled function's return value.
        """
        was_tracing = tracemalloc.is_tracing()
        if not was_tracing:
            tracemalloc.start(trace_depth)

        try:
            (
                current_before,
                peak_before,
                rss_before,
                before,
            ) = MemoryProfiler.prepare_profile(
                collect_garbage=collect_garbage,
                compare_allocations=compare_allocations,
                include_rss=include_rss,
            )

            started = time.perf_counter()
            error = None

            try:
                return func(*args, **kwargs)

            except BaseException as exc:
                error = exc
                raise

            finally:
                try:
                    report = MemoryProfiler.build_report(
                        function=getattr(
                            func,
                            "__qualname__",
                            repr(func),
                        ),
                        started=started,
                        current_before=current_before,
                        peak_before=peak_before,
                        rss_before=rss_before,
                        before=before,
                        top=top,
                        compare_by=compare_by,
                        include_rss=include_rss,
                        error=error,
                    )
                except Exception as exc:
                    warnings.warn(
                        f"Memory profiling report creation failed: {exc}",
                        RuntimeWarning,
                        stacklevel=2,
                    )
                else:
                    MemoryProfiler._emit_safely(
                        report,
                        log_to_console=log_to_console,
                        logger=logger,
                        callback=callback,
                    )

        finally:
            if not was_tracing and tracemalloc.is_tracing():
                tracemalloc.stop()

    @staticmethod
    async def _profile_async(
        func: Callable,
        args: tuple,
        kwargs: dict,
        *,
        log_to_console: bool,
        top: int,
        trace_depth: int,
        collect_garbage: bool,
        include_rss: bool,
        compare_allocations: bool,
        logger: logging.Logger | None,
        callback: Callable[[MemoryReport], Any] | None,
        compare_by: str,
    ) -> Any:
        """
        Execute an asynchronous function and collect memory statistics.

        Returns:
            The awaited function's result.
        """
        was_tracing = tracemalloc.is_tracing()
        if not was_tracing:
            tracemalloc.start(trace_depth)

        try:
            (
                current_before,
                peak_before,
                rss_before,
                before,
            ) = MemoryProfiler.prepare_profile(
                collect_garbage=collect_garbage,
                compare_allocations=compare_allocations,
                include_rss=include_rss,
            )

            started = time.perf_counter()
            error = None

            try:
                return await func(*args, **kwargs)

            except BaseException as exc:
                error = exc
                raise

            finally:
                try:
                    report = MemoryProfiler.build_report(
                        function=getattr(
                            func,
                            "__qualname__",
                            repr(func),
                        ),
                        started=started,
                        current_before=current_before,
                        peak_before=peak_before,
                        rss_before=rss_before,
                        before=before,
                        top=top,
                        compare_by=compare_by,
                        include_rss=include_rss,
                        error=error,
                    )
                except Exception as exc:
                    warnings.warn(
                        f"Memory profiling report creation failed: {exc}",
                        RuntimeWarning,
                        stacklevel=2,
                    )
                else:
                    MemoryProfiler._emit_safely(
                        report,
                        log_to_console=log_to_console,
                        logger=logger,
                        callback=callback,
                    )

        finally:
            if not was_tracing and tracemalloc.is_tracing():
                tracemalloc.stop()

    @staticmethod
    def track_memory(
        func: Callable | None = None,
        *,
        args: tuple = (),
        kwargs: dict | None = None,
        log_to_console: bool = True,
        top: int = 10,
        trace_depth: int = 25,
        collect_garbage: bool = False,
        include_rss: bool = True,
        compare_allocations: bool = True,
        logger: logging.Logger | None = None,
        callback: Callable[[MemoryReport], Any] | None = None,
        compare_by: str = "lineno",
    ) -> Any:
        """
        Profile a function's memory usage.

        Supports direct invocation and decorator usage.

        Args:
            func: Function to profile. If omitted, returns a decorator.
            args: Positional arguments for direct invocation only.
            kwargs: Keyword arguments for direct invocation only.
            log_to_console: Print the memory report.
            top: Maximum number of allocation differences to display.
            trace_depth: Number of traceback frames tracked by tracemalloc.
            collect_garbage: Collect unreachable objects before profiling.
            include_rss: Include process RSS measurements when available.
            compare_allocations: Compare allocation snapshots.
            logger: Optional Python logger.
            callback: Optional synchronous callable receiving a MemoryReport.
            compare_by: Grouping strategy: lineno, filename, or traceback.

        Returns:
            Function result for direct invocation, or a wrapped function
            when used as a decorator.

        Raises:
            ValueError: Invalid profiling configuration.
            TypeError: Invalid function, arguments, or callback.
        """
        if top < 0:
            raise ValueError("top must be non-negative")

        if trace_depth < 1:
            raise ValueError("trace_depth must be positive")

        if compare_by not in {
            "lineno",
            "filename",
            "traceback",
        }:
            raise ValueError(
                "compare_by must be lineno, filename, or traceback"
            )

        if not isinstance(args, tuple):
            raise TypeError("args must be a tuple")

        if kwargs is not None and not isinstance(kwargs, dict):
            raise TypeError("kwargs must be a dictionary")

        if callback is not None and not callable(callback):
            raise TypeError("callback must be callable")

        if logger is not None and not isinstance(logger, logging.Logger):
            raise TypeError("logger must be a logging.Logger instance")

        if func is not None and (args or kwargs) and not callable(func):
            raise TypeError("func must be callable")

        options = {
            "log_to_console": log_to_console,
            "top": top,
            "trace_depth": trace_depth,
            "collect_garbage": collect_garbage,
            "include_rss": include_rss,
            "compare_allocations": compare_allocations,
            "logger": logger,
            "callback": callback,
            "compare_by": compare_by,
        }

        def decorator(target: Callable) -> Callable:
            """
            Wrap a function with memory profiling.

            Args:
                target: Function to wrap.

            Returns:
                Synchronous or asynchronous profiling wrapper.
            """
            if not callable(target):
                raise TypeError("track_memory expects a callable")

            if inspect.isgeneratorfunction(target):
                raise TypeError(
                    "Generator functions are not supported directly. "
                    "Profile their iteration instead."
                )

            if inspect.isasyncgenfunction(target):
                raise TypeError(
                    "Async generators are not supported directly. "
                    "Profile their iteration instead."
                )

            if inspect.iscoroutinefunction(target):

                @functools.wraps(target)
                async def async_wrapper(
                    *func_args: Any,
                    **func_kwargs: Any,
                ) -> Any:
                    return await MemoryProfiler._profile_async(
                        target,
                        func_args,
                        func_kwargs,
                        **options,
                    )

                return async_wrapper

            @functools.wraps(target)
            def wrapper(
                *func_args: Any,
                **func_kwargs: Any,
            ) -> Any:
                return MemoryProfiler._profile(
                    target,
                    func_args,
                    func_kwargs,
                    **options,
                )

            return wrapper

        if func is None:
            if args or kwargs:
                raise ValueError(
                    "args and kwargs are only valid with direct invocation"
                )

            return decorator

        if not callable(func):
            raise TypeError("func must be callable")

        # Direct invocation:
        # track_memory(my_function, args=(...), kwargs={...})
        wrapped = decorator(func)

        if inspect.iscoroutinefunction(func):
            return wrapped(*(args or ()), **(kwargs or {}))

        return wrapped(*(args or ()), **(kwargs or {}))
