# import redis.asyncio as aioredis
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import BaseStorage
# from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.memory  import MemoryStorage

from src.core.settings import BotSettings, RedisSettings
from src.core.logger import log



def load_bot(settings: BotSettings) -> Bot:
    log.info("Setup bot... ")
    return Bot(**settings.model_dump())


def load_storage(settings: RedisSettings) -> MemoryStorage:
    log.info("Setup storage... ")
    # return RedisStorage(redis=aioredis.Redis(**settings.model_dump()))
    return MemoryStorage()


def load_dispatcher(storage: BaseStorage) -> Dispatcher:
    log.info("Setup dispatcher... ")
    return Dispatcher(storage=storage)
