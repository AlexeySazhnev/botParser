from aiogram import F, Router

from src.routers.client.callbacks.extension import (
    back_callback,
    paginate_next_callback,
    paginate_previous_callback,
)
from src.routers.client.callbacks.user import phone_callback, phones_list_callback


def register_callbacks(router: Router) -> None:
    router.callback_query.register(back_callback, F.data == "back")
    router.callback_query.register(paginate_next_callback, F.data == "next")
    router.callback_query.register(paginate_previous_callback, F.data == "previous")
    router.callback_query.register(phones_list_callback, F.data == "phones_list")
    router.callback_query.register(phone_callback, F.data.regexp(r"current_phone:.*"))
