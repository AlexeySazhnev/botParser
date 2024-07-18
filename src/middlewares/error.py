from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, types

from src.common.errors import MessageNotPresentError
from src.core.logger import log


class ErrorMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: types.TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except MessageNotPresentError:
            pass
        except Exception as e:
            log.exception(f"{e}")
            if isinstance(event, types.CallbackQuery):
                await event.answer(
                    "Something goes wrong, try to restart /start", show_alert=True
                )
                message = event.message
                if isinstance(message, types.Message):
                    await message.delete()
            if isinstance(event, types.Message):
                await event.answer("Something goes wrong, try to restart /start")
                await event.delete()
