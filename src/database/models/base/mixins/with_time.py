from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class ModelWithTimeMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(True), server_default=func.now(), onupdate=func.now()
    )
