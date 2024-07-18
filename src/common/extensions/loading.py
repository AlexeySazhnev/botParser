from functools import wraps
from typing import Awaitable, Callable, ParamSpec, TypeVar

from aiogram import types

P = ParamSpec("P")
R = TypeVar("R")


def on_loading(coro: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    @wraps(coro)
    async def _wrapper(*args: P.args, **kw: P.kwargs) -> R:
        update = kw.get("event_update")
        if not hasattr(update, "callback_query"):
            raise TypeError("'on_loading' should be using only with callback_query")

        message = update.callback_query.message
        if not isinstance(message, types.Message):
            raise TypeError("No message provided")

        await message.edit_text("loading... ")

        return await coro(*args, **kw)

    return _wrapper


