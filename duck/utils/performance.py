"""
Performance Utilities Module

Provides functions for measuring code performance, timing code execution, 
and optimizing operations.
"""
import time

from duck.logging import console # better than print()


def exec_time(func):
    """
    A decorator that measures the execution time of a function.
    
    Args:
        func (function): The function to measure.
    
    Returns:
        function: The wrapped function that will time its execution.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        console.log_raw(f'Execution time: "{func.__name__}": {(end_time - start_time)/1000:.8f} ms')
        return result
    return wrapper


def async_exec_time(func):
    """
    A decorator that measures the execution time of a function.
    
    Args:
        func (function): The function to measure.
    
    Returns:
        function: The wrapped asynchronous function that will time its execution.
    """
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        console.log_raw(f'Execution time: "{func.__name__}": {(end_time - start_time)/1000:.8f} ms')
        return result
    return async_wrapper


def measure_time(func):
    """
    Measures the time taken to run a function.
    
    Args:
        func (function): The function to measure.
    
    Returns:
        float: The execution time in seconds.
    """
    start_time = time.time()
    func()
    end_time = time.time()
    return end_time - start_time


def optimize_list_sort(lst: list) -> list:
    """
    Optimizes sorting by removing duplicates before sorting the list.
    
    Args:
        lst (list): The list to be sorted.
    
    Returns:
        list: The sorted list without duplicates.
    """
    return sorted(set(lst))
