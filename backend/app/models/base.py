from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, func
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from backend.app.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class PrimaryKeyMixin:
    id: Mapped[int] = mapped_column(primary_key=True)


class TableNameMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class ModelBase(Base, PrimaryKeyMixin, TimestampMixin, TableNameMixin):
    __abstract__ = True


def money_column(*, nullable: bool = False, default: Decimal | None = None) -> Mapped[Decimal]:
    return mapped_column(Numeric(12, 2), nullable=nullable, default=default)


def quantity_column(*, nullable: bool = False, default: Decimal | None = None) -> Mapped[Decimal]:
    return mapped_column(Numeric(12, 3), nullable=nullable, default=default)
