from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Client:
    """Represents a client profile in the booking system."""

    id: UUID
    user_id: UUID
    full_name: str
    phone: str | None = None

    def __post_init__(self) -> None:
        if not self.full_name.strip():
            raise ValueError("Client name cannot be empty.")
