from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Service:
    """Represents a service offered by the salon."""

    id: UUID
    name: str
    duration_minutes: int
    price: Decimal
    description: str | None = None
    is_active: bool = True

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Service name cannot be empty.")

        if self.duration_minutes <= 0:
            raise ValueError("Service duration must be positive.")

        if not self.price.is_finite() or self.price < Decimal("0"):
            raise ValueError("Service price must be a finite non-negative value.")
