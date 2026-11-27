from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Service:
    """Represents a service offered by the salon."""

    id: UUID
    name: str
    duration_minutes: int
    price: int
    description: str | None = None
    is_active: bool = True

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Service name cannot be empty.")
        if self.duration_minutes <= 0:
            raise ValueError("Service duration must be positive.")
        if self.price < 0:
            raise ValueError("Service price cannot be negative.")
