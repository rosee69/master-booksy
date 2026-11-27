from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
)
from sqlalchemy import (
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from master_booksy.adapters.database.base import Base
from master_booksy.domain.enums.appointment_status import AppointmentStatus


class AppointmentModel(Base):
    __tablename__ = "appointments"

    __table_args__ = (
        CheckConstraint(
            "starts_at < ends_at",
            name="valid_appointment_interval",
        ),
        CheckConstraint(
            "price_at_booking >= 0",
            name="non_negative_appointment_price",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    client_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="RESTRICT"),
        nullable=False,
    )

    master_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("masters.id", ondelete="RESTRICT"),
        nullable=False,
    )

    service_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="RESTRICT"),
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

    status: Mapped[AppointmentStatus] = mapped_column(
        SQLAlchemyEnum(
            AppointmentStatus,
            name="appointment_status",
            native_enum=False,
            length=20,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=AppointmentStatus.PENDING,
        nullable=False,
    )

    price_at_booking: Mapped[int] = mapped_column(
    Integer,
    default=0,
    nullable=False,
    )
    