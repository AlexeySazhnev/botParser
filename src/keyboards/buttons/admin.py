from typing import Any, Dict

from src.keyboards.buttons.button import button
from src.database.models import Phone



def back_button() -> Dict[str, Any]:
    return button(text="Back", callback_data="back")


def admin_panel_button() -> Dict[str, Any]:
    return button(text="Admin", callback_data="admin_panel")


def pars_phones_button() -> Dict[str, Any]:
    return button(text="Pars_phones 📲", callback_data="pars_phones")


def del_button(phone: Phone) -> Dict[str, Any]:
    return button(text="Delete", callback_data=f"delete_phone:{phone.id}")