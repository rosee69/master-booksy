from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Master:
    """Represents a master profile in the booking system."""

    id: UUID
    user_id: UUID
    display_name: str
    bio: str | None = None
    is_active: bool = True

    def __post_init__(self) -> None:
        if not self.display_name.strip():
            raise ValueError("Master name cannot be empty.")
