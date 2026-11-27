from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from master_booksy.adapters.database.models.appointment_model import (
    AppointmentModel,
)
from master_booksy.adapters.repositories.base import BaseRepository
from master_booksy.domain.entities.appointment import Appointment
from master_booksy.domain.enums.appointment_status import AppointmentStatus


class AppointmentRepository(BaseRepository):
    """Repository for managing appointments."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, appointment_id: UUID) -> Appointment | None:
        """Get an appointment by its ID."""
        result = await self.session.execute(
            select(AppointmentModel).where(
                AppointmentModel.id == appointment_id
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_client_id(
        self,
        client_id: UUID,
    ) -> list[Appointment]:
        """Get all appointments belonging to a client."""
        result = await self.session.execute(
            select(AppointmentModel)
            .where(AppointmentModel.client_id == client_id)
            .order_by(AppointmentModel.starts_at)
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def get_by_master_id(
        self,
        master_id: UUID,
    ) -> list[Appointment]:
        """Get all appointments assigned to a master."""
        result = await self.session.execute(
            select(AppointmentModel)
            .where(AppointmentModel.master_id == master_id)
            .order_by(AppointmentModel.starts_at)
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def get_by_master_and_period(
        self,
        master_id: UUID,
        period_start: datetime,
        period_end: datetime,
    ) -> list[Appointment]:
        """Get a master's appointments overlapping a time period."""
        result = await self.session.execute(
            select(AppointmentModel)
            .where(
                AppointmentModel.master_id == master_id,
                AppointmentModel.starts_at < period_end,
                AppointmentModel.ends_at > period_start,
            )
            .order_by(AppointmentModel.starts_at)
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def get_overlapping(
        self,
        master_id: UUID,
        starts_at: datetime,
        ends_at: datetime,
        exclude_appointment_id: UUID | None = None,
    ) -> list[Appointment]:
        """Get active appointments overlapping the specified interval."""
        query = select(AppointmentModel).where(
            AppointmentModel.master_id == master_id,
            AppointmentModel.starts_at < ends_at,
            AppointmentModel.ends_at > starts_at,
            AppointmentModel.status != AppointmentStatus.CANCELLED,
        )

        if exclude_appointment_id is not None:
            query = query.where(
                AppointmentModel.id != exclude_appointment_id
            )

        result = await self.session.execute(
            query.order_by(AppointmentModel.starts_at)
        )
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def create(self, appointment: Appointment) -> Appointment:
        """Create a new appointment."""
        model = AppointmentModel(
            id=appointment.id,
            client_id=appointment.client_id,
            master_id=appointment.master_id,
            service_id=appointment.service_id,
            starts_at=appointment.starts_at,
            ends_at=appointment.ends_at,
            status=appointment.status,
            price_at_booking=appointment.price_at_booking,
        )

        self.session.add(model)
        await self.session.flush()

        return self._to_entity(model)

    async def update(
        self,
        appointment: Appointment,
    ) -> Appointment | None:
        """Update an existing appointment."""
        result = await self.session.execute(
            select(AppointmentModel).where(
                AppointmentModel.id == appointment.id
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        model.client_id = appointment.client_id
        model.master_id = appointment.master_id
        model.service_id = appointment.service_id
        model.starts_at = appointment.starts_at
        model.ends_at = appointment.ends_at
        model.status = appointment.status
        model.price_at_booking = appointment.price_at_booking

        await self.session.flush()

        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: AppointmentModel) -> Appointment:
        """Convert an ORM model into a domain entity."""
        return Appointment(
            id=model.id,
            client_id=model.client_id,
            master_id=model.master_id,
            service_id=model.service_id,
            starts_at=model.starts_at,
            ends_at=model.ends_at,
            status=model.status,
            price_at_booking=model.price_at_booking,
        )
