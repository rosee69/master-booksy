from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from master_booksy.adapters.database.base import Base
from master_booksy.adapters.database.models.master_model import MasterModel


class TimeOffModel(Base):
    """SQLAlchemy model for master's unavailable periods."""

    __tablename__ = "time_offs"

    __table_args__ = (
        CheckConstraint(
            "starts_at < ends_at",
            name="valid_time_off_interval",
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
    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    ends_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    master: Mapped[MasterModel] = relationship(
        back_populates="time_offs",
    )
