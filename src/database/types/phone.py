from typing import TypedDict

from typing_extensions import Required


class CreatePhoneType(TypedDict):
    name: Required[str]
    price: Required[str]
    url: Required[str]


class UpdatePhoneType(TypedDict):
    name: Required[str]
    price: Required[str]
    url: Required[str]
