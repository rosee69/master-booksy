from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from master_booksy.domain.enums.appointment_status import AppointmentStatus


@dataclass(frozen=True, slots=True)
class Appointment:
    """Represents a client's appointment with a master."""

    id: UUID
    client_id: UUID
    master_id: UUID
    service_id: UUID
    starts_at: datetime
    ends_at: datetime
    status: AppointmentStatus = AppointmentStatus.PENDING
    price_at_booking: int = 0

    def __post_init__(self) -> None:
        if self.starts_at >= self.ends_at:
            raise ValueError("Appointment end must be later than its start.")

        if self.starts_at.tzinfo is None or self.ends_at.tzinfo is None:
            raise ValueError("Appointment datetimes must be timezone-aware.")

        if self.starts_at.utcoffset() is None or self.ends_at.utcoffset() is None:
            raise ValueError("Appointment datetimes must have a valid UTC offset.")

        if self.price_at_booking < 0:
            raise ValueError("Appointment price must be non-negative.")
