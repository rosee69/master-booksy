from datetime import time
from uuid import uuid4

import pytest

from master_booksy.adapters.repositories.master_repository import (
    MasterRepository,
)
from master_booksy.adapters.repositories.schedule_repository import (
    ScheduleRepository,
)
from master_booksy.adapters.repositories.user_repository import UserRepository
from master_booksy.domain.entities.master import Master
from master_booksy.domain.entities.schedule import Schedule
from master_booksy.domain.entities.user import User
from master_booksy.domain.enums.user_role import UserRole


async def create_test_master(db_session) -> Master:
    user = User(
        id=uuid4(),
        email="master@example.com",
        password_hash="hashed-password",
        role=UserRole.MASTER,
    )
    await UserRepository(db_session).create(user)

    master = Master(
        id=uuid4(),
        user_id=user.id,
        display_name="Mile Phakphum",
    )
    return await MasterRepository(db_session).create(master)


async def create_test_schedule(
    repository: ScheduleRepository,
    master_id,
    weekday: int = 0,
    opens_at: time = time(9, 0),
    closes_at: time = time(18, 0),
) -> Schedule:
    schedule = Schedule(
        id=uuid4(),
        master_id=master_id,
        weekday=weekday,
        opens_at=opens_at,
        closes_at=closes_at,
    )
    return await repository.create(schedule)


@pytest.mark.asyncio
async def test_create_schedule(db_session):
    repository = ScheduleRepository(db_session)
    master = await create_test_master(db_session)

    schedule = await create_test_schedule(repository, master.id)

    assert schedule.master_id == master.id
    assert schedule.weekday == 0
    assert schedule.opens_at == time(9, 0)
    assert schedule.closes_at == time(18, 0)


@pytest.mark.asyncio
async def test_get_schedule_by_id(db_session):
    repository = ScheduleRepository(db_session)
    master = await create_test_master(db_session)
    schedule = await create_test_schedule(repository, master.id)

    found_schedule = await repository.get_by_id(schedule.id)
    missing_schedule = await repository.get_by_id(uuid4())

    assert found_schedule == schedule
    assert missing_schedule is None


@pytest.mark.asyncio
async def test_get_schedules_by_master_id(db_session):
    repository = ScheduleRepository(db_session)
    master = await create_test_master(db_session)

    monday = await create_test_schedule(
        repository,
        master.id,
        weekday=0,
    )
    tuesday = await create_test_schedule(
        repository,
        master.id,
        weekday=1,
    )

    schedules = await repository.get_by_master_id(master.id)

    assert schedules == [monday, tuesday]


@pytest.mark.asyncio
async def test_get_schedules_by_master_and_weekday(db_session):
    repository = ScheduleRepository(db_session)
    master = await create_test_master(db_session)

    await create_test_schedule(
        repository,
        master.id,
        weekday=1,
        opens_at=time(9, 0),
        closes_at=time(13, 0),
    )
    afternoon = await create_test_schedule(
        repository,
        master.id,
        weekday=1,
        opens_at=time(14, 0),
        closes_at=time(18, 0),
    )
    await create_test_schedule(
        repository,
        master.id,
        weekday=2,
    )

    schedules = await repository.get_by_master_and_weekday(
        master.id,
        1,
    )

    assert len(schedules) == 2
    assert schedules[0].opens_at == time(9, 0)
    assert schedules[1] == afternoon


@pytest.mark.asyncio
async def test_update_schedule(db_session):
    repository = ScheduleRepository(db_session)
    master = await create_test_master(db_session)
    schedule = await create_test_schedule(repository, master.id)

    updated_schedule = Schedule(
        id=schedule.id,
        master_id=master.id,
        weekday=0,
        opens_at=time(10, 0),
        closes_at=time(19, 0),
    )

    result = await repository.update(updated_schedule)

    missing_schedule = Schedule(
        id=uuid4(),
        master_id=master.id,
        weekday=0,
        opens_at=time(9, 0),
        closes_at=time(18, 0),
    )
    missing_result = await repository.update(missing_schedule)

    assert result == updated_schedule
    assert missing_result is None


@pytest.mark.asyncio
async def test_delete_schedule(db_session):
    repository = ScheduleRepository(db_session)
    master = await create_test_master(db_session)
    schedule = await create_test_schedule(repository, master.id)

    result = await repository.delete(schedule.id)

    assert result is True
    assert await repository.get_by_id(schedule.id) is None


@pytest.mark.asyncio
async def test_delete_schedule_returns_false_when_not_found(db_session):
    repository = ScheduleRepository(db_session)

    result = await repository.delete(uuid4())

    assert result is False
