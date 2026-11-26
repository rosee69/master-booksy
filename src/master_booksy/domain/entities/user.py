from dataclasses import dataclass
from uuid import UUID

from master_booksy.domain.enums.user_role import UserRole


@dataclass(frozen=True, slots=True)
class User:
    """Represents a user account in the booking system."""

    id: UUID
    email: str
    password_hash: str
    role: UserRole
    is_active: bool = True

    def __post_init__(self) -> None:
        if not self.email.strip():
            raise ValueError("Email cannot be empty.")

        if not self.password_hash.strip():
            raise ValueError("Password hash cannot be empty.")
