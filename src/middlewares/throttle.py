import asyncio
from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict, Final, Optional, Tuple

from aiogram import BaseMiddleware
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import CallbackQuery, Message, TelegramObject

TRIGGER_VALUE: Final[int] = 3
MESSAGE_TIMOUT: Final[int] = 10
CALLBACK_TIMEOUT: Final[int] = 1


async def delete_key(data: Dict[str, Any], key: str, timeout: int) -> None:
    if not data.get(key):
        return None
    await asyncio.sleep(timeout)
    data.pop(key, None)


class ThrottleMiddleware(BaseMiddleware):
    __slots__ = ("_storage", "_memory_storage")

    def __init__(self, storage: BaseStorage) -> None:
        self._storage = storage
        self._memory_storage: Dict[str, Any] = defaultdict(lambda: 0)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(self._storage, MemoryStorage):
            return await self.throttle_memory(self._storage, handler, event, data)
        if isinstance(self._storage, RedisStorage):
            return await self.throttle_redis(self._storage, handler, event, data)

    async def throttle_memory(
        self,
        _: MemoryStorage,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        throttle_data = self._get_timeout_message_and_key(event)
        if not throttle_data:
            return None

        user_key, message, timeout = throttle_data

        is_throttled = self._memory_storage.get(user_key)
        try:
            if is_throttled:
                count = int(is_throttled)
                if count == TRIGGER_VALUE:
                    self._memory_storage[user_key] += 1
                    if isinstance(event, CallbackQuery):
                        return await event.answer(message, show_alert=True)
                    elif isinstance(event, Message):
                        return await event.answer(message)
                elif count > TRIGGER_VALUE:
                    return
                else:
                    self._memory_storage[user_key] += 1
            else:
                self._memory_storage.setdefault(user_key, 1)
        finally:
            asyncio.create_task(delete_key(self._memory_storage, user_key, timeout))
        return await handler(event, data)

    async def throttle_redis(
        self,
        storage: RedisStorage,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        throttle_data = self._get_timeout_message_and_key(event)
        if not throttle_data:
            return None

        user_key, message, timeout = throttle_data

        is_throttled = await storage.redis.get(user_key)
        if is_throttled:
            count = int(is_throttled)
            if count == TRIGGER_VALUE:
                await storage.redis.set(user_key, value=count + 1, ex=timeout)
                if isinstance(event, CallbackQuery):
                    return await event.answer(message, show_alert=True)
                elif isinstance(event, Message):
                    return await event.answer(message)
            elif count > TRIGGER_VALUE:
                return
            else:
                await storage.redis.set(user_key, value=count + 1, ex=timeout)
        else:
            await storage.redis.set(user_key, value=1, ex=timeout)

        return await handler(event, data)

    def _get_timeout_message_and_key(
        self, event: TelegramObject
    ) -> Optional[Tuple[str, str, int]]:
        if isinstance(event, CallbackQuery):
            event_message = event.message
            if isinstance(event_message, Message):
                user_key = f"callback_{event.from_user.id}:{event_message.chat.id}"
            else:
                user_key = f"callback_{event.from_user.id}"

            timeout = CALLBACK_TIMEOUT
            message = "Dont spam on buttons please"
        elif isinstance(event, Message):
            user = event.from_user
            if not user:
                user_key = f"message_{event.chat.id}"
            else:
                user_key = f"message_{user.id}:{event.chat.id}"

            timeout = MESSAGE_TIMOUT
            message = "Dont spam please"
        else:
            return None

        return (user_key, message, timeout)
