from typing import Any, Callable, List

from aiogram import types
from aiogram.fsm.context import FSMContext

from src.common.extensions import Chat, Pagination
from src.database.gateway import DBGateway
from src.keyboards import build_markup
from src.keyboards.buttons import admin_panel_button, phones_list_button


async def start_message(
    message: types.Message,
    state: FSMContext,
    chat: Chat,
    identifier: str,
    pagination: Pagination,
    user: types.User,
    admins: List[int],
    gateway: Callable[[], DBGateway],
    **_: Any,
) -> None:
    user_data = user.model_dump(
        exclude={
            "added_to_attachment_menu",
            "can_join_groups",
            "can_read_all_group_messages",
            "supports_inline_queries",
            "can_connect_to_business",
        }
    )

    async with gateway() as gw:
        repo = gw.user()
        exists = await repo.exists(user.id)
        if not exists:
            await repo.create(**user_data)
        else:
            await repo.update(user.id, **user_data)

    buttons = [phones_list_button()]
    if user.id in admins:
        buttons += [admin_panel_button()]

    await message.answer(
        "Hello 👋🏻\nHere are your phones",
        reply_markup=build_markup(*buttons),
    )

    chat.set_callback(identifier, start_message, True)
    pagination.clear(identifier)
    await state.set_state()
