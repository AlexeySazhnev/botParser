from aiogram import BaseMiddleware, Router

from src.middlewares.chat import ChatMiddleware
from src.middlewares.error import ErrorMiddleware
from src.middlewares.throttle import ThrottleMiddleware

__all__ = (
    "ThrottleMiddleware",
    "ChatMiddleware",
    "ErrorMiddleware",
)


def setup_middlewares(
    router: Router, *middlewares: BaseMiddleware, is_outer: bool
) -> None:
    for middleware in middlewares:
        if is_outer:
            router.message.outer_middleware(middleware)
            router.callback_query.outer_middleware(middleware)
        else:
            router.message.middleware(middleware)
            router.callback_query.middleware(middleware)
