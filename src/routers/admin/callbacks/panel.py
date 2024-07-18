import logging
from typing import Any, Callable, List

from aiogram import types

from src.common.extensions import CallbackType, Pagination
from src.common.extensions.handle import call_as_message
from src.common.youla.core import YoulaAPI
from src.database.gateway import DBGateway
from src.database.models import User
from src.keyboards import build_markup
from src.keyboards.buttons import (
    back_button,
    current_user_button,
    next_pagination_button,
    paginate_users_button,
    pars_phones_button,
    previous_pagination_button,
)


async def current_user_callback(
    call: types.CallbackQuery, gateway: Callable[[], DBGateway], **kw: Any
) -> CallbackType:
    message = await call_as_message(call)
    user_id = int(call.data.split(":")[-1]) if call.data else 0

    gw = gateway()
    async with gw.manager.session:
        user = await gw.user().get(user_id)

    if not user:
        text = "This user no longer exists"
    else:
        text = (
            f'ID: {user.id}\n'
            f'User name: {user.first_name}\n'
            f'User username: {user.username or "Without username"}'
        )

    await message.edit_text(text=text, reply_markup=build_markup(back_button()))

    return current_user_callback


async def paginate_users_callback(
    call: types.CallbackQuery,
    pagination: Pagination,
    identifier: str,
    gateway: Callable[[], DBGateway],
    **kw: Any,
) -> CallbackType:
    message = await call_as_message(call)

    async def paginate(offset: int, limit: int) -> List[User]:
        gw = gateway()
        async with gw.manager.session:
            return await gw.user().get_many(offset=offset, limit=limit)

    data = pagination.get(identifier)
    page = 0
    if data:
        page = data.current_page - 1

    shared_text = "<strong>Users List</strong>"
    data = pagination.add(
        id=identifier,
        data_func=current_user_button,
        paginate_func=paginate,  # type: ignore
        shared_text=shared_text,
        page=page,
    )

    if not await data.is_next_exists():
        data.current_page = 0

    buttons = [current_user_button(user) for user in await data.next()]

    if buttons:
        if await data.is_previous_exists():
            buttons += [previous_pagination_button()]
        if await data.is_next_exists():
            buttons += [next_pagination_button()]

        buttons += [back_button()]
    else:
        buttons += [back_button()]

    await message.edit_text(text=shared_text, reply_markup=build_markup(*buttons))

    return paginate_users_callback


async def admin_panel_callback(call: types.CallbackQuery, **_: Any) -> CallbackType:
    message = await call_as_message(call)
    await message.edit_text(
        text="You are in admin panel",
        reply_markup=build_markup(
            pars_phones_button(),
            paginate_users_button(),
            back_button(),
        ),
    )
    return admin_panel_callback


async def admin_pars_phone_callback(
    call: types.CallbackQuery, gateway: Callable[[], DBGateway], **_: Any
) -> CallbackType:
    message = await call_as_message(call)
    await message.edit_text(
        text="Parsing of products in the database",
        reply_markup=build_markup(back_button()),
    )
    async with gateway() as gw:
        repo = gw.phone()
        await repo.delete()
        async with YoulaAPI() as youla:
            # data = await youla.iter_catalog_products_board().collect()
            async for item in youla.iter_catalog_products_board():
                data = item["data"]["feed"]["items"]
                for card in data:
                    try:
                        name = card["product"]["name"]
                        price = card["product"]["price"]["realPriceText"]
                        url = "https://youla.ru" + card["product"]["url"]
                        await repo.create(name=name, price=price, url=url)

                    except KeyError:
                        logging.error("The key is missing")
    return admin_pars_phone_callback


async def admin_del_phone_callback(
    call: types.CallbackQuery, gateway: Callable[[], DBGateway], **_: Any
) -> None:
    message = await call_as_message(call)
    phone_id = int(call.data.split(":")[-1]) if call.data else 0
    print(phone_id)
    await message.edit_text(
        text="Your product has been deleted 📵",
        reply_markup=build_markup(back_button()),
    )
    async with gateway() as gw:
        repo = gw.phone()
        await repo.delete(phone_id)


        
    # return admin_del_phone_callback
