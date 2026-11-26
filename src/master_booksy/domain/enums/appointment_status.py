from enum import StrEnum


class AppointmentStatus(StrEnum):
    """Possible states of an appointment."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
