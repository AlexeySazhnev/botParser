from typing import List, Union

from aiogram import types
from aiogram.filters import Filter


class IsAdmin(Filter):
    def __init__(self, admins: List[int]) -> None:
        self._admins = admins

    async def __call__(self, event: Union[types.CallbackQuery, types.Message]) -> bool:
        if event.from_user.id not in self._admins: # type: ignore
            await event.answer("You have not permission to do that")
            return False

        return True
