from typing import Any

from aiogram import types
from aiogram.fsm.context import FSMContext

from src.common.extensions import Chat, Pagination, call_as_message
from src.routers.client.commands import start_message
from src.common.errors import PaginatorWasNotSetError
from src.keyboards.buttons import back_button, next_pagination_button, previous_pagination_button
from src.keyboards import build_markup



async def back_callback(
    call: types.CallbackQuery,
    chat: Chat,
    state: FSMContext,
    identifier: str,
    **kw: Any,
) -> None:
    message = call.message

    if not isinstance(message, types.Message):
        return None
    callback = chat.get_callback(identifier)

    if not callback:
        await message.delete()
        await start_message(
            message=message, state=state, chat=chat, identifier=identifier, **kw
        )
    else:
        callback_name = callback.__name__

        if callback_name.endswith("message"):
            if callback_name == "start_message":
                await message.delete()
            await callback(message, chat=chat, state=state, identifier=identifier, **kw)
        else:
            await callback(call, chat=chat, state=state, identifier=identifier, **kw)

    await state.set_state()


async def paginate_next_callback(
    call: types.CallbackQuery, pagination: Pagination, identifier: str, **_: Any
) -> None:
    data = pagination.get(identifier)
    if not data:
        raise PaginatorWasNotSetError("Paginator was not set")

    buttons = [
        await data.data_func(elem) if data.is_data_func_async else data.data_func(elem)
        for elem in await data.next()
    ]
    buttons += [previous_pagination_button()]
    if await data.is_next_exists():
        buttons += [next_pagination_button()]

    buttons += [back_button()]
    message = await call_as_message(call)
    await message.edit_text(
        text=data.shared_text, reply_markup=build_markup(*buttons)
    )


async def paginate_previous_callback(
    call: types.CallbackQuery, pagination: Pagination, identifier: str, **_: Any
) -> None:
    data = pagination.get(identifier)
    if not data:
        raise PaginatorWasNotSetError("Paginator was not set")

    buttons = [
        await data.data_func(elem) if data.is_data_func_async else data.data_func(elem)
        for elem in await data.previous()
    ]

    if await data.is_previous_exists():
        buttons += [
            previous_pagination_button(),
            next_pagination_button(),
            back_button(),
        ]
    else:
        buttons += [next_pagination_button(), back_button()]
    message = await call_as_message(call)
    await message.edit_text(text=data.shared_text, reply_markup=build_markup(*buttons))