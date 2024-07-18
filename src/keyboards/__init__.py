from typing import (
    Any,
    Callable,
    Dict,
    Final,
    List,
    Tuple,
    TypeGuard,
    overload,
)

from aiogram import types

from src.keyboards.default import dafault_keyboard, get_default_button
from src.keyboards.inline import get_inline_button, inline_keyboard

__all__ = (
    "get_default_button",
    "dafault_keyboard",
    "inline_keyboard",
    "get_inline_button",
    "build_buttons",
    "build_markup",
    "is_dict_type",
    "is_str_type",
)

DEFAULT_SEP: Final[int] = 2



def is_dict_type(
    data: Tuple[Dict[str, Any], ...],
) -> TypeGuard[Tuple[Dict[str, Any], ...]]:
    is_all_true = [isinstance(t, dict) for t in data]

    return all(is_all_true)


def is_str_type(data: Tuple[str, ...]) -> TypeGuard[Tuple[str, ...]]:
    is_all_true = [isinstance(t, str) for t in data]

    return all(is_all_true)


@overload
def build_buttons(
    *, buttons: List[types.KeyboardButton], sep: int = DEFAULT_SEP
) -> List[List[types.KeyboardButton]]: ...
@overload
def build_buttons(
    *, buttons: List[types.InlineKeyboardButton], sep: int = DEFAULT_SEP
) -> List[List[types.InlineKeyboardButton]]: ...
def build_buttons(*, buttons: Any, sep: int = DEFAULT_SEP) -> Any:
    return [buttons[n : n + sep] for n in range(0, len(buttons), sep)]


@overload
def build_markup( # type: ignore
    *buttons: Dict[str, Any],
    keyboard: Callable[..., types.InlineKeyboardMarkup] = inline_keyboard,
    button: Callable[..., types.InlineKeyboardButton] = get_inline_button,
    sep: int = DEFAULT_SEP,
) -> types.InlineKeyboardMarkup: ...
@overload
def build_markup(
    *buttons: Dict[str, Any],
    keyboard: Callable[..., types.ReplyKeyboardMarkup] = dafault_keyboard,
    button: Callable[..., types.KeyboardButton] = get_default_button,
    sep: int = DEFAULT_SEP,
) -> types.ReplyKeyboardMarkup: ...
def build_markup(
    *buttons: Dict[str, Any],
    keyboard: Any = inline_keyboard,
    button: Any = get_inline_button,
    sep: int = DEFAULT_SEP,
) -> Any:
    if not all([callable(button), callable(keyboard)]):
        raise TypeError("keyboard and button params should be callable type")

    if not is_dict_type(buttons):
        raise ValueError("buttons params should be dict type")

    return keyboard(
        build_buttons(buttons=[button(**value) for value in buttons], sep=sep)
    )