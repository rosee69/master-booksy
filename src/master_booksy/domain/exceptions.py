class DomainError(Exception):
    """Base exception for business logic errors."""


class SlotUnavailableError(DomainError):
    """Raised when the requested time slot is unavailable."""


class OutsideWorkingHoursError(DomainError):
    """Raised when an appointment is outside the master's working hours."""


class ScheduleExceptionError(DomainError):
    """Raised when an appointment overlaps with a schedule exception."""


class MasterServiceMismatchError(DomainError):
    """Raised when a master does not provide the requested service."""


class InvalidAppointmentStateError(DomainError):
    """Raised when an appointment cannot transition to the requested state."""
