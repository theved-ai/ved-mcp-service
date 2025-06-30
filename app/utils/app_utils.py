from __future__ import annotations

from mcp import types
from datetime import datetime
from typing import Callable, TypeVar, Union, Awaitable
from zoneinfo import ZoneInfo

from app.config.logging_config import logger


def current_time_ist():
    return datetime.now(tz=ZoneInfo('Asia/Kolkata'))

def ensure(predicate: Callable[[], bool], exception: str) -> None:
    """
    Evaluate predicate(); if it returns False, raise the given exception.
    """
    if not predicate():
        logger.error(exception)

async def ensure_async(predicate: Callable[[], Awaitable[bool]], exception: str) -> None:
    """
    Evaluate predicate()in async; if it returns False, raise the given exception.
    """
    if not await predicate():
        logger.error(exception)


T = TypeVar("T")

def execute_if_or_else(
        predicate: bool,
        if_fn: Callable[[], Union[T, None]],
        else_fn: Callable[[], Union[T, None]]
) -> T:
    """
    Lazily execute one of two callables based on the boolean predicate.
    """
    return if_fn() if predicate else else_fn()


async def execute_try_catch_async(
        try_fn: Callable[[], Awaitable[T]],
        catch_fn: Callable[[Exception], None]
) -> T | None:
    """
    Executes the async try_fn. If it raises, catch_fn(exc) is called
    to produce a new Exception which is then raised.
    """
    try:
        return await try_fn()
    except Exception as e:
        catch_fn(e)
        return None

async def execute_try_catch_async_no_raised_exception(
        try_fn: Callable[[], Awaitable[T]],
        catch_fn: Callable[[Exception], Awaitable[T]]
) -> T:
    """
    Executes the async try_fn. If it raises, catch_fn(exc) is called
    to produce a new Exception which is then raised.
    """
    try:
        return await try_fn()
    except Exception as e:
        return await catch_fn(e)

async def failed_tool_response(e, msg):
    logger.exception(msg)
    return types.CallToolResult(isError=True, content=[types.TextContent(type="text", text=str(e))])