import uuid

from sqlalchemy import UUID, BigInteger, Integer, text
from sqlalchemy.orm import Mapped, mapped_column


class ModelWithIntegerIDMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)


class ModelWithBigIntegerIDMixin:
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)


class ModelWIthUUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
