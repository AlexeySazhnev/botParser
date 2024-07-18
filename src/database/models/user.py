from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from src.database.models.base import Base
from src.database.models.base.mixins import (
    ModelWithBigIntegerIDMixin,
    ModelWithTimeMixin,
)




class User(Base, ModelWithTimeMixin, ModelWithBigIntegerIDMixin):
    is_bot: Mapped[bool]
    first_name: Mapped[str]
    last_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    username: Mapped[Optional[str]] = mapped_column(nullable=True)
    language_code: Mapped[Optional[str]] = mapped_column(nullable=True)
    is_premium: Mapped[Optional[bool]] = mapped_column(nullable=True)
    
