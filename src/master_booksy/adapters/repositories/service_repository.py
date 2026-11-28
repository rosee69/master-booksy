from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from master_booksy.adapters.database.models.service_model import ServiceModel
from master_booksy.adapters.repositories.base import BaseRepository
from master_booksy.domain.entities.service import Service


class ServiceRepository(BaseRepository):
    """Repository for managing salon services."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, service_id: UUID) -> Service | None:
        result = await self.session.execute(
            select(ServiceModel).where(ServiceModel.id == service_id)
        )
        service_model = result.scalar_one_or_none()

        if service_model is None:
            return None

        return self._to_entity(service_model)

    async def get_all(self) -> list[Service]:
        result = await self.session.execute(select(ServiceModel))
        service_models = result.scalars().all()

        return [self._to_entity(model) for model in service_models]

    async def get_active(self) -> list[Service]:
        result = await self.session.execute(
            select(ServiceModel).where(ServiceModel.is_active.is_(True))
        )
        service_models = result.scalars().all()

        return [self._to_entity(model) for model in service_models]

    async def get_by_master_id(self, master_id: UUID) -> list[Service]:
        result = await self.session.execute(
            select(ServiceModel).where(ServiceModel.masters.any(id=master_id))
        )
        service_models = result.scalars().all()

        return [self._to_entity(model) for model in service_models]

    async def get_active_by_master_id(
        self,
        master_id: UUID,
    ) -> list[Service]:
        result = await self.session.execute(
            select(ServiceModel).where(
                ServiceModel.is_active.is_(True),
                ServiceModel.masters.any(id=master_id),
            )
        )
        service_models = result.scalars().all()

        return [self._to_entity(model) for model in service_models]

    async def create(self, service: Service) -> Service:
        service_model = ServiceModel(
            id=service.id,
            name=service.name,
            description=service.description,
            duration_minutes=service.duration_minutes,
            price=service.price,
            is_active=service.is_active,
        )
        self.session.add(service_model)
        await self.session.flush()

        return self._to_entity(service_model)

    async def update(self, service: Service) -> Service | None:
        result = await self.session.execute(
            select(ServiceModel).where(ServiceModel.id == service.id)
        )
        service_model = result.scalar_one_or_none()

        if service_model is None:
            return None

        service_model.name = service.name
        service_model.description = service.description
        service_model.duration_minutes = service.duration_minutes
        service_model.price = service.price
        service_model.is_active = service.is_active

        await self.session.flush()

        return self._to_entity(service_model)

    async def deactivate(self, service_id: UUID) -> Service | None:
        result = await self.session.execute(
            select(ServiceModel).where(ServiceModel.id == service_id)
        )
        service_model = result.scalar_one_or_none()

        if service_model is None:
            return None

        service_model.is_active = False
        await self.session.flush()

        return self._to_entity(service_model)

    async def exists_by_name(self, name: str) -> bool:
        result = await self.session.execute(
            select(ServiceModel.id).where(ServiceModel.name == name)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    def _to_entity(service_model: ServiceModel) -> Service:
        return Service(
            id=service_model.id,
            name=service_model.name,
            duration_minutes=service_model.duration_minutes,
            price=service_model.price,
            description=service_model.description,
            is_active=service_model.is_active,
        )
