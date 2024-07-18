import asyncio

from aiogram import Dispatcher, Router
from aiogram import types

from src.common.extensions import Chat, Pagination
from src.core import load_settings, log
from src.core.loader import load_bot, load_dispatcher, load_storage
from src.database.core.connection import create_sa_engine, create_sa_session_factory
from src.database.gateway import create_gateway_lazy
from src.middlewares import (
    ChatMiddleware,
    ErrorMiddleware,
    ThrottleMiddleware,
    setup_middlewares,
)
from src.routers import setup_main_router
from src.routers.admin import setup_admin_router
from src.routers.client import setup_client_router


def setup_routers(dp: Dispatcher, *routers: Router) -> None:
    dp.include_routers(*routers)


async def main() -> None:
    settings = load_settings()
    storage = load_storage(settings.redis)
    bot = load_bot(settings.bot)
    dp = load_dispatcher(storage)
    main_router = setup_main_router(
        setup_admin_router(settings.admin.list),
        setup_client_router(),
    )
    setup_routers(dp, main_router)
    setup_middlewares(
        main_router, ThrottleMiddleware(storage), ErrorMiddleware(), is_outer=True
    )
    setup_middlewares(main_router, ChatMiddleware(), is_outer=False)
    engine = create_sa_engine(settings.db.url)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(
        [
            types.BotCommand(
                command='/start',
                description='Starting iteract with bot'
            )
        ]
    )
    try:
        log.info("Starting bot... ")
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            chat=Chat(),
            pagination=Pagination(),
            admins=settings.admin.list,
            gateway=create_gateway_lazy(create_sa_session_factory(engine)),
        )
    except KeyboardInterrupt:
        log.info("Disabling bot... ")
    finally:
        log.info("Bot is disabled")
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("The bot has finished its work")
