from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from master_booksy.adapters.database.models.master_model import MasterModel
from master_booksy.adapters.repositories.base import BaseRepository
from master_booksy.domain.entities.master import Master


class MasterRepository(BaseRepository):
    """Repository for managing master profiles."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, master_id: UUID) -> Master | None:
        result = await self.session.execute(select(MasterModel).where(MasterModel.id == master_id))
        master_model = result.scalar_one_or_none()

        if master_model is None:
            return None

        return self._to_entity(master_model)

    async def get_by_user_id(self, user_id: UUID) -> Master | None:
        result = await self.session.execute(
            select(MasterModel).where(MasterModel.user_id == user_id)
        )
        master_model = result.scalar_one_or_none()

        if master_model is None:
            return None

        return self._to_entity(master_model)

    async def create(self, master: Master) -> Master:
        master_model = MasterModel(
            id=master.id,
            user_id=master.user_id,
            display_name=master.display_name,
            bio=master.bio,
            is_active=master.is_active,
        )

        self.session.add(master_model)
        await self.session.flush()

        return self._to_entity(master_model)

    @staticmethod
    def _to_entity(master_model: MasterModel) -> Master:
        return Master(
            id=master_model.id,
            user_id=master_model.user_id,
            display_name=master_model.display_name,
            bio=master_model.bio,
            is_active=master_model.is_active,
        )
