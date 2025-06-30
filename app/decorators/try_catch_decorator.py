import functools
from typing import Callable, Awaitable, Any
from app.utils.app_utils import execute_try_catch_async, execute_try_catch_async_no_raised_exception


def try_catch_wrapper(logger_fn: Callable[[Exception], None]):
    def decorator(func):
        @functools.wraps(func)
        async def wrapped(self, *args, **kwargs):
            async def try_fn():
                return await func(self, *args, **kwargs)

            return await execute_try_catch_async(
                try_fn=try_fn,
                catch_fn=logger_fn
            )
        return wrapped
    return decorator

def try_catch_wrapper_no_raised_exception(logger_fn: Callable[[Exception], Awaitable[Any]]):
    def decorator(func):
        @functools.wraps(func)
        async def wrapped(self, *args, **kwargs):
            async def try_fn():
                return await func(self, *args, **kwargs)

            return await execute_try_catch_async_no_raised_exception(
                try_fn=try_fn,
                catch_fn=logger_fn
            )
        return wrapped
    return decorator
