from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message
from src.common.extensions import Chat


class ChatMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        
        chat: Chat = data["chat"]
        if isinstance(event, CallbackQuery):
            message = event.message
            data['user'] = event.from_user
            if isinstance(message, Message):
                identifier = f'{event.from_user.id}:{message.chat.id}'
            else:
                identifier = f'{event.from_user.id}'
        elif isinstance(event, Message):
            user = event.from_user
            if user:
                identifier = f"{user.id}:{event.chat.id}"
                data['user'] = user
            else:
                identifier = f"{event.chat.id}"
        else:
            return None
        
        data['identifier'] = identifier
        
        result = await handler(event, data)
        if result and callable(result):
            chat.set_callback(identifier, result)
