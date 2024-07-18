from aiogram import Router
from aiogram.filters import CommandStart

from src.routers.client.commands.start import start_message

__all__ = ("start_message",)


def register_commands(router: Router) -> None:
    router.message.register(start_message, CommandStart())
