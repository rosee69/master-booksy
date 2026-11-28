from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest

from master_booksy.adapters.repositories.master_repository import (
    MasterRepository,
)
from master_booksy.adapters.repositories.time_off_repository import (
    TimeOffRepository,
)
from master_booksy.adapters.repositories.user_repository import UserRepository
from master_booksy.domain.entities.master import Master
from master_booksy.domain.entities.time_off import TimeOff
from master_booksy.domain.entities.user import User
from master_booksy.domain.enums.user_role import UserRole

BANGKOK_TZ = ZoneInfo("Asia/Bangkok")


async def create_test_master(
    db_session,
    email: str = "master@example.com",
) -> Master:
    user = User(
        id=uuid4(),
        email=email,
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


async def create_test_time_off(
    repository: TimeOffRepository,
    master_id,
    starts_at: datetime | None = None,
    ends_at: datetime | None = None,
    reason: str | None = "Vacation",
) -> TimeOff:
    time_off = TimeOff(
        id=uuid4(),
        master_id=master_id,
        starts_at=starts_at or datetime(2026, 8, 10, 9, 0, tzinfo=BANGKOK_TZ),
        ends_at=ends_at or datetime(2026, 8, 12, 18, 0, tzinfo=BANGKOK_TZ),
        reason=reason,
    )
    return await repository.create(time_off)


@pytest.mark.asyncio
async def test_create_time_off(db_session):
    repository = TimeOffRepository(db_session)
    master = await create_test_master(db_session)

    time_off = await create_test_time_off(repository, master.id)

    assert time_off.master_id == master.id
    assert time_off.reason == "Vacation"
    assert time_off.starts_at < time_off.ends_at


@pytest.mark.asyncio
async def test_get_time_off_by_id(db_session):
    repository = TimeOffRepository(db_session)
    master = await create_test_master(db_session)
    time_off = await create_test_time_off(repository, master.id)

    found_time_off = await repository.get_by_id(time_off.id)
    missing_time_off = await repository.get_by_id(uuid4())

    assert found_time_off == time_off
    assert missing_time_off is None


@pytest.mark.asyncio
async def test_get_time_offs_by_master_id(db_session):
    repository = TimeOffRepository(db_session)
    master = await create_test_master(db_session)

    first_time_off = await create_test_time_off(
        repository,
        master.id,
    )
    second_time_off = await create_test_time_off(
        repository,
        master.id,
        starts_at=datetime(2026, 8, 20, 9, 0, tzinfo=BANGKOK_TZ),
        ends_at=datetime(2026, 8, 22, 18, 0, tzinfo=BANGKOK_TZ),
        reason="Personal leave",
    )

    time_offs = await repository.get_by_master_id(master.id)

    assert time_offs == [first_time_off, second_time_off]


@pytest.mark.asyncio
async def test_get_time_offs_by_master_and_period(db_session):
    repository = TimeOffRepository(db_session)
    master = await create_test_master(db_session)

    overlapping_time_off = await create_test_time_off(
        repository,
        master.id,
    )
    await create_test_time_off(
        repository,
        master.id,
        starts_at=datetime(2026, 8, 20, 9, 0, tzinfo=BANGKOK_TZ),
        ends_at=datetime(2026, 8, 22, 18, 0, tzinfo=BANGKOK_TZ),
    )

    time_offs = await repository.get_by_master_and_period(
        master.id,
        datetime(2026, 8, 11, 0, 0, tzinfo=BANGKOK_TZ),
        datetime(2026, 8, 15, 0, 0, tzinfo=BANGKOK_TZ),
    )

    assert time_offs == [overlapping_time_off]


@pytest.mark.asyncio
async def test_update_time_off(db_session):
    repository = TimeOffRepository(db_session)
    master = await create_test_master(db_session)
    time_off = await create_test_time_off(repository, master.id)

    updated_time_off = TimeOff(
        id=time_off.id,
        master_id=master.id,
        starts_at=datetime(2026, 8, 15, 9, 0, tzinfo=BANGKOK_TZ),
        ends_at=datetime(2026, 8, 17, 18, 0, tzinfo=BANGKOK_TZ),
        reason="Updated vacation",
    )

    result = await repository.update(updated_time_off)

    missing_time_off = TimeOff(
        id=uuid4(),
        master_id=master.id,
        starts_at=datetime(2026, 8, 15, 9, 0, tzinfo=BANGKOK_TZ),
        ends_at=datetime(2026, 8, 17, 18, 0, tzinfo=BANGKOK_TZ),
    )
    missing_result = await repository.update(missing_time_off)

    assert result == updated_time_off
    assert missing_result is None


@pytest.mark.asyncio
async def test_delete_time_off(db_session):
    repository = TimeOffRepository(db_session)
    master = await create_test_master(db_session)
    time_off = await create_test_time_off(repository, master.id)

    result = await repository.delete(time_off.id)

    assert result is True
    assert await repository.get_by_id(time_off.id) is None


@pytest.mark.asyncio
async def test_delete_time_off_returns_false_when_not_found(db_session):
    repository = TimeOffRepository(db_session)

    result = await repository.delete(uuid4())

    assert result is False


@pytest.mark.asyncio
async def test_get_time_offs_by_master_and_period_returns_empty_list(
    db_session,
):
    repository = TimeOffRepository(db_session)
    master = await create_test_master(db_session)

    await create_test_time_off(repository, master.id)

    time_offs = await repository.get_by_master_and_period(
        master.id,
        datetime(2026, 8, 20, 0, 0, tzinfo=BANGKOK_TZ),
        datetime(2026, 8, 25, 0, 0, tzinfo=BANGKOK_TZ),
    )

    assert time_offs == []


@pytest.mark.asyncio
async def test_get_time_offs_returns_only_selected_master_periods(
    db_session,
):
    repository = TimeOffRepository(db_session)

    first_master = await create_test_master(db_session)
    second_master = await create_test_master(
        db_session,
        email="second_master@example.com",
    )

    first_time_off = await create_test_time_off(
        repository,
        first_master.id,
    )
    await create_test_time_off(
        repository,
        second_master.id,
    )

    time_offs = await repository.get_by_master_id(first_master.id)

    assert time_offs == [first_time_off]
