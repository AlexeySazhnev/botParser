from typing import List

from aiogram import Router

from src.core.logger import log
from src.routers.admin.callbacks import register_callbacks
from src.routers.admin.commands import register_commands
from src.routers.admin.messages import register_messages


def setup_admin_router(admins: List[int]) -> Router:
    log.info("Setup admin router... ")
    router = Router(name="admin")
    register_callbacks(router, admins)
    register_commands(router, admins)
    register_messages(router, admins)

    return router
