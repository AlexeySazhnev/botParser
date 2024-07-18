from typing import Literal

from src.database.types.phone import CreatePhoneType, UpdatePhoneType
from src.database.types.user import CreateUserType, UpdateUserType

OrderByType = Literal["ASC", "DESC"]

__all__ = ("CreateUserType", "UpdateUserType", "CreatePhoneType", "UpdatePhoneType")
