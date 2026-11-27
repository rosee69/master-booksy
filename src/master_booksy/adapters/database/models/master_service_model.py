from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from master_booksy.adapters.database.base import Base

master_services = Table(
    "master_services",
    Base.metadata,
    Column(
        "master_id",
        PG_UUID(as_uuid=True),
        ForeignKey("masters.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "service_id",
        PG_UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
