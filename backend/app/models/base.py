import uuid
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from app.db.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UUIDMixin:
    @declared_attr.directive
    def id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        )


class BaseModel(UUIDMixin, TimestampMixin, Base):
    __abstract__ = True