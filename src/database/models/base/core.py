import re
from typing import Any, Dict

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    __abstract__: bool = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()

    def __repr__(self) -> str:
        params = ", ".join(
            f"{attr}={value!r}"
            for attr, value in self.__dict__.items()
            if not attr.startswith("_")
        )
        return f"{type(self).__name__}({params})"

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {}

        for attr, value in self.__dict__.items():
            if attr.startswith("_"):
                continue
            if isinstance(value, Base):
                result[attr] = value.to_dict()
            elif isinstance(value, (list, tuple)):
                result[attr] = type(value)(
                    v.to_dict() if isinstance(v, Base) else v for v in value
                )
            else:
                result[attr] = value

        return result
