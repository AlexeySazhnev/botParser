from aiogram import types
from aiogram.filters import Filter


class IsValidNumberType(Filter):
    async def __call__(self, event: types.Message) -> bool:
        try:
            text = event.text
            if not text:
                return False
            float(text.replace(",", "."))
        except ValueError:
            await event.answer('Enter a valid number please')
            return False

        return True

