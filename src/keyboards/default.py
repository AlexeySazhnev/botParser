from typing import List, Optional, Any

from aiogram import types




def dafault_keyboard(
    reply_keyboard: List[List[types.KeyboardButton]],
    resize_keyboard: Optional[bool] = True,
    one_time_keyboard: Optional[bool] = None,
    **kw: Any
) -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=reply_keyboard,
        resize_keyboard=resize_keyboard,
        one_time_keyboard=one_time_keyboard,
        **kw
    )
    

def get_default_button(
        text: str,
        **kw: Any
) -> types.KeyboardButton:
    return types.KeyboardButton(
        text=text,
        **kw
    )
