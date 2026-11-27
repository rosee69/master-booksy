from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from master_booksy.adapters.database.models.time_off_model import TimeOffModel
from master_booksy.adapters.repositories.base import BaseRepository
from master_booksy.domain.entities.time_off import TimeOff


class TimeOffRepository(BaseRepository):
    """Repository for managing master's unavailable periods."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, time_off_id: UUID) -> TimeOff | None:
        result = await self.session.execute(
            select(TimeOffModel).where(TimeOffModel.id == time_off_id)
        )
        time_off_model = result.scalar_one_or_none()

        if time_off_model is None:
            return None

        return self._to_entity(time_off_model)

    async def get_by_master_id(self, master_id: UUID) -> list[TimeOff]:
        result = await self.session.execute(
            select(TimeOffModel)
            .where(TimeOffModel.master_id == master_id)
            .order_by(TimeOffModel.starts_at)
        )
        time_off_models = result.scalars().all()

        return [self._to_entity(model) for model in time_off_models]

    async def get_by_master_and_period(
        self,
        master_id: UUID,
        period_start: datetime,
        period_end: datetime,
    ) -> list[TimeOff]:
        result = await self.session.execute(
            select(TimeOffModel)
            .where(
                TimeOffModel.master_id == master_id,
                TimeOffModel.starts_at < period_end,
                TimeOffModel.ends_at > period_start,
            )
            .order_by(TimeOffModel.starts_at)
        )
        time_off_models = result.scalars().all()

        return [self._to_entity(model) for model in time_off_models]

    async def create(self, time_off: TimeOff) -> TimeOff:
        time_off_model = TimeOffModel(
            id=time_off.id,
            master_id=time_off.master_id,
            starts_at=time_off.starts_at,
            ends_at=time_off.ends_at,
            reason=time_off.reason,
        )
        self.session.add(time_off_model)
        await self.session.flush()

        return self._to_entity(time_off_model)

    async def update(self, time_off: TimeOff) -> TimeOff | None:
        result = await self.session.execute(
            select(TimeOffModel).where(TimeOffModel.id == time_off.id)
        )
        time_off_model = result.scalar_one_or_none()

        if time_off_model is None:
            return None

        time_off_model.master_id = time_off.master_id
        time_off_model.starts_at = time_off.starts_at
        time_off_model.ends_at = time_off.ends_at
        time_off_model.reason = time_off.reason

        await self.session.flush()

        return self._to_entity(time_off_model)

    async def delete(self, time_off_id: UUID) -> bool:
        result = await self.session.execute(
            select(TimeOffModel).where(TimeOffModel.id == time_off_id)
        )
        time_off_model = result.scalar_one_or_none()

        if time_off_model is None:
            return False

        await self.session.delete(time_off_model)
        await self.session.flush()

        return True

    @staticmethod
    def _to_entity(time_off_model: TimeOffModel) -> TimeOff:
        return TimeOff(
            id=time_off_model.id,
            master_id=time_off_model.master_id,
            starts_at=time_off_model.starts_at,
            ends_at=time_off_model.ends_at,
            reason=time_off_model.reason,
        )
