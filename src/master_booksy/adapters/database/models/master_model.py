from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from master_booksy.adapters.database.base import Base
from master_booksy.adapters.database.models.master_service_model import (
    master_services,
)
from master_booksy.adapters.database.models.user_model import UserModel

if TYPE_CHECKING:
    from master_booksy.adapters.database.models.schedule_model import ScheduleModel
    from master_booksy.adapters.database.models.service_model import ServiceModel
    from master_booksy.adapters.database.models.time_off_model import TimeOffModel


class MasterModel(Base):
    """SQLAlchemy model for master profiles."""

    __tablename__ = "masters"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    user: Mapped[UserModel] = relationship()
    services: Mapped[list[ServiceModel]] = relationship(
        secondary=master_services,
        back_populates="masters",
    )
    schedules: Mapped[list[ScheduleModel]] = relationship(
    back_populates="master",
    cascade="all, delete-orphan",
    )
    time_offs: Mapped[list[TimeOffModel]] = relationship(
    back_populates="master",
    cascade="all, delete-orphan",
)
