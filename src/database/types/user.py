from typing import TypedDict, Optional

from typing_extensions import Required, NotRequired



class CreateUserType(TypedDict):
    id: Required[int]
    is_bot: Required[bool]
    first_name: Required[str]
    last_name: NotRequired[Optional[str]]
    username: NotRequired[Optional[str]]
    language_code: NotRequired[Optional[str]]
    is_premium: NotRequired[Optional[bool]]



class UpdateUserType(TypedDict):
    is_bot: NotRequired[bool]
    first_name: NotRequired[str]
    last_name: NotRequired[Optional[str]]
    username: NotRequired[Optional[str]]
    language_code: NotRequired[Optional[str]]
    is_premium: NotRequired[Optional[bool]]
    