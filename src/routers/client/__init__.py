from aiogram import Router

from src.core.logger import log
from src.routers.client.callbacks import register_callbacks
from src.routers.client.commands import register_commands
from src.routers.client.messages import register_messages


def setup_client_router() -> Router:
    log.info("Setup client router... ")
    router = Router(name="client")
    register_commands(router)
    register_callbacks(router)
    register_messages(router)

    return router
