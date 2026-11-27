
from uuid import uuid4

import pytest

from master_booksy.adapters.repositories.client_repository import (
    ClientRepository,
)
from master_booksy.adapters.repositories.user_repository import UserRepository
from master_booksy.domain.entities.client import Client
from master_booksy.domain.entities.user import User
from master_booksy.domain.enums.user_role import UserRole


@pytest.mark.asyncio
async def test_create_client(db_session):
    user = User(
        id=uuid4(),
        email="dunk@example.com",
        password_hash="hashed-password",
        role=UserRole.CLIENT,
    )
    client = Client(
        id=uuid4(),
        user_id=user.id,
        full_name="Natachai Boonprasert",
        phone="+66123456789",
    )

    await UserRepository(db_session).create(user)
    repository = ClientRepository(db_session)

    created_client = await repository.create(client)

    assert created_client == client


@pytest.mark.asyncio
async def test_get_client_by_id(db_session):
    user = User(
        id=uuid4(),
        email="noeul@example.com",
        password_hash="hashed-password",
        role=UserRole.CLIENT,
    )
    client = Client(
        id=uuid4(),
        user_id=user.id,
        full_name="Nuttarat Tangwai",
    )

    await UserRepository(db_session).create(user)
    repository = ClientRepository(db_session)

    await repository.create(client)
    found_client = await repository.get_by_id(client.id)

    assert found_client == client


@pytest.mark.asyncio
async def test_get_client_by_user_id(db_session):
    user = User(
        id=uuid4(),
        email="dunk_noeul@example.com",
        password_hash="hashed-password",
        role=UserRole.CLIENT,
    )
    client = Client(
        id=uuid4(),
        user_id=user.id,
        full_name="Dunk Natachai and Noeul Nuttarat",
        phone="+66987654321",
    )

    await UserRepository(db_session).create(user)
    repository = ClientRepository(db_session)

    await repository.create(client)
    found_client = await repository.get_by_user_id(user.id)

    assert found_client == client


@pytest.mark.asyncio
async def test_get_client_by_id_returns_none_when_not_found(db_session):
    repository = ClientRepository(db_session)

    found_client = await repository.get_by_id(uuid4())

    assert found_client is None


@pytest.mark.asyncio
async def test_get_client_by_user_id_returns_none_when_not_found(db_session):
    repository = ClientRepository(db_session)

    found_client = await repository.get_by_user_id(uuid4())

    assert found_client is None
