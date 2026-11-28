from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from master_booksy.adapters.database.models.schedule_model import ScheduleModel
from master_booksy.adapters.repositories.base import BaseRepository
from master_booksy.domain.entities.schedule import Schedule


class ScheduleRepository(BaseRepository):
    """Repository for managing master's working schedules."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, schedule_id: UUID) -> Schedule | None:
        result = await self.session.execute(
            select(ScheduleModel).where(ScheduleModel.id == schedule_id)
        )
        schedule_model = result.scalar_one_or_none()

        if schedule_model is None:
            return None

        return self._to_entity(schedule_model)

    async def get_by_master_id(self, master_id: UUID) -> list[Schedule]:
        result = await self.session.execute(
            select(ScheduleModel)
            .where(ScheduleModel.master_id == master_id)
            .order_by(ScheduleModel.weekday)
        )
        schedule_models = result.scalars().all()

        return [self._to_entity(model) for model in schedule_models]

    async def get_by_master_and_weekday(
        self,
        master_id: UUID,
        weekday: int,
    ) -> list[Schedule]:
        result = await self.session.execute(
            select(ScheduleModel)
            .where(
                ScheduleModel.master_id == master_id,
                ScheduleModel.weekday == weekday,
            )
            .order_by(ScheduleModel.opens_at)
        )
        schedule_models = result.scalars().all()

        return [self._to_entity(model) for model in schedule_models]

    async def create(self, schedule: Schedule) -> Schedule:
        schedule_model = ScheduleModel(
            id=schedule.id,
            master_id=schedule.master_id,
            weekday=schedule.weekday,
            opens_at=schedule.opens_at,
            closes_at=schedule.closes_at,
        )
        self.session.add(schedule_model)
        await self.session.flush()

        return self._to_entity(schedule_model)

    async def update(self, schedule: Schedule) -> Schedule | None:
        result = await self.session.execute(
            select(ScheduleModel).where(ScheduleModel.id == schedule.id)
        )
        schedule_model = result.scalar_one_or_none()

        if schedule_model is None:
            return None

        schedule_model.master_id = schedule.master_id
        schedule_model.weekday = schedule.weekday
        schedule_model.opens_at = schedule.opens_at
        schedule_model.closes_at = schedule.closes_at

        await self.session.flush()

        return self._to_entity(schedule_model)

    async def delete(self, schedule_id: UUID) -> bool:
        result = await self.session.execute(
            select(ScheduleModel).where(ScheduleModel.id == schedule_id)
        )
        schedule_model = result.scalar_one_or_none()

        if schedule_model is None:
            return False

        await self.session.delete(schedule_model)
        await self.session.flush()

        return True

    @staticmethod
    def _to_entity(schedule_model: ScheduleModel) -> Schedule:
        return Schedule(
            id=schedule_model.id,
            master_id=schedule_model.master_id,
            weekday=schedule_model.weekday,
            opens_at=schedule_model.opens_at,
            closes_at=schedule_model.closes_at,
        )
