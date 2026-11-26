from enum import StrEnum


class UserRole(StrEnum):
    """Roles available in the booking system."""

    CLIENT = "client"
    MASTER = "master"
    ADMIN = "admin"
