from __future__ import annotations

from datetime import time
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Time
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from master_booksy.adapters.database.base import Base
from master_booksy.adapters.database.models.master_model import MasterModel


class ScheduleModel(Base):
    """SQLAlchemy model for a master's working schedule."""

    __tablename__ = "schedules"

    __table_args__ = (
        CheckConstraint(
            "weekday >= 0 AND weekday <= 6",
            name="weekday_range",
        ),
        CheckConstraint(
            "opens_at < closes_at",
            name="valid_working_interval",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    master_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("masters.id", ondelete="CASCADE"),
        nullable=False,
    )
    weekday: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    opens_at: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )
    closes_at: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    master: Mapped[MasterModel] = relationship(
        back_populates="schedules",
    )
