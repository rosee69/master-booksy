from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class TimeOff:
    """Represents a period when a master is unavailable."""

    id: UUID
    master_id: UUID
    starts_at: datetime
    ends_at: datetime
    reason: str | None = None

    def __post_init__(self) -> None:
        if self.starts_at >= self.ends_at:
            raise ValueError("Time off end must be later than its start.")

        if self.starts_at.tzinfo is None or self.ends_at.tzinfo is None:
            raise ValueError("Time off datetimes must be timezone-aware.")

        if self.starts_at.utcoffset() is None or self.ends_at.utcoffset() is None:
            raise ValueError("Time off datetimes must have a valid UTC offset.")
