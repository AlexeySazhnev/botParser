from typing import List

from aiogram import F, Router

from src.filters import IsAdmin
from src.routers.admin.callbacks.panel import (
    admin_panel_callback,
    admin_pars_phone_callback,
    admin_del_phone_callback,
    current_user_callback,
    paginate_users_callback,
)


def register_callbacks(router: Router, admins: List[int]) -> None:
    router.callback_query.register(
        admin_panel_callback, F.data == "admin_panel", IsAdmin(admins)
    )
    router.callback_query.register(
        admin_pars_phone_callback, F.data == "pars_phones", IsAdmin(admins)
    )
 
    router.callback_query.register(
        paginate_users_callback, F.data == "paginate_users", IsAdmin(admins)
    )
    router.callback_query.register(
        current_user_callback, F.data.regexp(r"current_user:.*"), IsAdmin(admins)
    )
    router.callback_query.register(
        admin_del_phone_callback, F.data.regexp(r"delete_phone:.*"), IsAdmin(admins)
    )