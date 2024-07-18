from typing import List, Optional, Any, Union

from aiogram import types
from aiogram.filters.callback_data import CallbackData



def inline_keyboard(
    inline_buttons: List[List[types.InlineKeyboardButton]],
    **kw: Any
) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(inline_keyboard=inline_buttons, **kw)


def get_inline_button(
    text: str,
    callback_data: Optional[Union[str, CallbackData]] = None,
    url: Optional[str] = None,
    wep_app: Optional[types.WebAppInfo] = None,
    **kw: Any
) -> types.InlineKeyboardButton:
    return types.InlineKeyboardButton(
        text=text,
        callback_data=callback_data.pack() if isinstance(callback_data, CallbackData) else callback_data,
        url=url,
        web_app=wep_app,
        **kw
    )

