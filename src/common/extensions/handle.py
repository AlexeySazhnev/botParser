from aiogram import types

from src.common.errors import MessageNotPresentError


async def call_as_message(call:types.CallbackQuery, on_error_message: str = 'Error') -> types.Message: 
    
    if not isinstance(call.message, types.Message):
        await call.answer(on_error_message)
        raise MessageNotPresentError('Message not present')
    return call.message
