from typing import Any, Callable, List

from aiogram import types

from src.common.extensions import CallbackType, Pagination, call_as_message
from src.database.gateway import DBGateway
from src.database.models import Phone
from src.keyboards import build_markup
from src.keyboards.buttons import (
    back_button,
    del_button,
    next_pagination_button,
    phone_button,
    previous_pagination_button,
)


async def phones_list_callback(
    call: types.CallbackQuery,
    pagination: Pagination,
    identifier: str,
    gateway: Callable[[], DBGateway],
    **kw: Any,
) -> CallbackType:
    message = await call_as_message(call)

    async def paginate(offset: int, limit: int) -> List[Phone]:
        gw = gateway()
        async with gw.manager.session:
            return await gw.phone().get_many(offset=offset, limit=limit)

    data = pagination.get(identifier)
    page = 0
    if data:
        page = data.current_page - 1

    shared_text = "<strong>Phones List</strong>"
    data = pagination.add(
        id=identifier,
        data_func=phone_button,
        paginate_func=paginate,  # type: ignore
        shared_text=shared_text,
        page=page,
    )

    if not await data.is_next_exists():
        data.current_page = 0

    buttons = [phone_button(phone) for phone in await data.next()]
    if buttons:
        if await data.is_previous_exists():
            buttons += [previous_pagination_button()]
        if await data.is_next_exists():
            buttons += [next_pagination_button()]

        buttons += [back_button()]
    else:
        buttons += [back_button()]

    await message.edit_text(text=shared_text, reply_markup=build_markup(*buttons))

    return phones_list_callback


async def phone_callback(
    call: types.CallbackQuery,
    user: types.User,
    admins: List[int],
    gateway: Callable[[], DBGateway],
    **kw: Any,
) -> CallbackType:
    message = await call_as_message(call)
    phone_id = int(call.data.split(":")[-1]) if call.data else 0

    gw = gateway()
    async with gw.manager.session:
        phone = await gw.phone().get(phone_id)

    if not phone:
        text = "This product no longer exists"
    else:
        text = (
            f"Phone name: {phone.name}\nPrice: {phone.price}\nURL: {phone.url}"
        )
    buttons = [back_button()]
    if user.id in admins:
        buttons += [del_button(phone)] # type: ignore
    await message.edit_text(text=text, reply_markup=build_markup(*buttons))

    return phone_callback
