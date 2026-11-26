from dataclasses import dataclass
from datetime import time
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Schedule:
    """Represents one working interval in a master's schedule."""

    id: UUID
    master_id: UUID
    weekday: int
    opens_at: time
    closes_at: time

    def __post_init__(self) -> None:
        if not 0 <= self.weekday <= 6:
            raise ValueError("Weekday must be between 0 and 6.")

        if self.opens_at >= self.closes_at:
            raise ValueError("Closing time must be later than opening time.")
