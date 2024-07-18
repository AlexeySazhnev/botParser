from aiogram import Router

from src.core.logger import log


def setup_main_router(*routers: Router) -> Router:
    log.info("Setup main router... ")
    router = Router(name="main")
    router.include_routers(*routers)

    return router
