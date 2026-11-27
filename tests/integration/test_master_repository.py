from uuid import uuid4

import pytest

from master_booksy.adapters.repositories.master_repository import (
    MasterRepository,
)
from master_booksy.adapters.repositories.user_repository import UserRepository
from master_booksy.domain.entities.master import Master
from master_booksy.domain.entities.user import User
from master_booksy.domain.enums.user_role import UserRole


@pytest.mark.asyncio
async def test_create_master(db_session):
    user = User(
        id=uuid4(),
        email="mile@example.com",
        password_hash="hashed-password",
        role=UserRole.MASTER,
    )
    master = Master(
        id=uuid4(),
        user_id=user.id,
        display_name="Mile Phakphum",
        bio="Professional beauty specialist.",
    )

    await UserRepository(db_session).create(user)
    repository = MasterRepository(db_session)

    created_master = await repository.create(master)

    assert created_master == master


@pytest.mark.asyncio
async def test_get_master_by_id(db_session):
    user = User(
        id=uuid4(),
        email="fort@example.com",
        password_hash="hashed-password",
        role=UserRole.MASTER,
    )
    master = Master(
        id=uuid4(),
        user_id=user.id,
        display_name="Fort Thitipong",
    )

    await UserRepository(db_session).create(user)
    repository = MasterRepository(db_session)

    await repository.create(master)
    found_master = await repository.get_by_id(master.id)

    assert found_master == master


@pytest.mark.asyncio
async def test_get_master_by_user_id(db_session):
    user = User(
        id=uuid4(),
        email="first@example.com",
        password_hash="hashed-password",
        role=UserRole.MASTER,
    )
    master = Master(
        id=uuid4(),
        user_id=user.id,
        display_name="First Kanaphan",
        bio="Experienced specialist.",
        is_active=False,
    )

    await UserRepository(db_session).create(user)
    repository = MasterRepository(db_session)

    await repository.create(master)
    found_master = await repository.get_by_user_id(user.id)

    assert found_master == master


@pytest.mark.asyncio
async def test_get_master_by_id_returns_none_when_not_found(db_session):
    repository = MasterRepository(db_session)

    found_master = await repository.get_by_id(uuid4())

    assert found_master is None


@pytest.mark.asyncio
async def test_get_master_by_user_id_returns_none_when_not_found(db_session):
    repository = MasterRepository(db_session)

    found_master = await repository.get_by_user_id(uuid4())

    assert found_master is None
