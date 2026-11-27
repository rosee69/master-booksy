import re

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr


def generate_table_name(class_name: str) -> str:
    """Convert a class name from CamelCase to snake_case."""
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", class_name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(table_name)s_%(column_0_name)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return generate_table_name(cls.__name__)
