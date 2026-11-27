from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from master_booksy.adapters.database.base import Base
from master_booksy.adapters.database.models.user_model import UserModel


class ClientModel(Base):
    """SQLAlchemy model for client profiles."""

    __tablename__ = "clients"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    user: Mapped[UserModel] = relationship()
