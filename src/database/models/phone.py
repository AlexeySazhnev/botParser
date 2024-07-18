from sqlalchemy.orm import Mapped

from src.database.models.base import Base
from src.database.models.base.mixins import ModelWithIntegerIDMixin


class Phone(Base, ModelWithIntegerIDMixin):
    name: Mapped[str]
    price: Mapped[str]
    url: Mapped[str]
