from typing import Dict, Any

from src.keyboards.buttons.button import button
from src.database.models import User, Phone


def back_button() -> Dict[str, Any]:
    return button(text='Back', callback_data='back')


def next_pagination_button() -> Dict[str, Any]:
    return button(text='>>', callback_data='next')


def previous_pagination_button() -> Dict[str, Any]:
    return button(text='<<', callback_data='previous')


def paginate_users_button() -> Dict[str, Any]:
    return button(text='Users List', callback_data='paginate_users')


def current_user_button(user: User) -> Dict[str, Any]:
    return button(text=f"User {user.id}", callback_data=f"current_user:{user.id}")


def phones_list_button() -> Dict[str, Any]:
    return button(text="Phones 📱", callback_data="phones_list")


def phone_button(phone: Phone) -> Dict[str, Any]:
    return button(text=f"{phone.name}", callback_data=f"current_phone:{phone.id}")
