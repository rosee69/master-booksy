from uuid import uuid4

import pytest

from master_booksy.adapters.repositories.user_repository import UserRepository
from master_booksy.domain.entities.user import User
from master_booksy.domain.enums.user_role import UserRole


@pytest.mark.asyncio
async def test_create_user(db_session):
    user = User(
        id=uuid4(),
        email="client@example.com",
        password_hash="hashed-password",
        role=UserRole.CLIENT,
    )

    repository = UserRepository(db_session)

    created_user = await repository.create(user)

    assert created_user == user


@pytest.mark.asyncio
async def test_get_user_by_id(db_session):
    user = User(
        id=uuid4(),
        email="master@example.com",
        password_hash="hashed-password",
        role=UserRole.MASTER,
    )

    repository = UserRepository(db_session)

    await repository.create(user)
    found_user = await repository.get_by_id(user.id)

    assert found_user == user


@pytest.mark.asyncio
async def test_get_user_by_email(db_session):
    user = User(
        id=uuid4(),
        email="admin@example.com",
        password_hash="hashed-password",
        role=UserRole.ADMIN,
    )

    repository = UserRepository(db_session)

    await repository.create(user)
    found_user = await repository.get_by_email(user.email)

    assert found_user == user


@pytest.mark.asyncio
async def test_get_user_by_id_returns_none_when_not_found(db_session):
    repository = UserRepository(db_session)

    found_user = await repository.get_by_id(uuid4())

    assert found_user is None


@pytest.mark.asyncio
async def test_get_user_by_email_returns_none_when_not_found(db_session):
    repository = UserRepository(db_session)

    found_user = await repository.get_by_email("unknown@example.com")

    assert found_user is None


@pytest.mark.asyncio
async def test_exists_by_email(db_session):
    user = User(
        id=uuid4(),
        email="existing@example.com",
        password_hash="hashed-password",
        role=UserRole.CLIENT,
    )

    repository = UserRepository(db_session)

    await repository.create(user)

    assert await repository.exists_by_email(user.email) is True
    assert await repository.exists_by_email("unknown@example.com") is False