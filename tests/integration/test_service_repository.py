from uuid import uuid4

import pytest
from sqlalchemy import insert

from master_booksy.adapters.database.models.master_service_model import (
    master_services,
)
from master_booksy.adapters.repositories.master_repository import (
    MasterRepository,
)
from master_booksy.adapters.repositories.service_repository import (
    ServiceRepository,
)
from master_booksy.adapters.repositories.user_repository import UserRepository
from master_booksy.domain.entities.master import Master
from master_booksy.domain.entities.service import Service
from master_booksy.domain.entities.user import User
from master_booksy.domain.enums.user_role import UserRole


async def create_test_service(
    repository: ServiceRepository,
    name: str = "Haircut",
    duration_minutes: int = 60,
    price: int = 500,
    is_active: bool = True,
) -> Service:
    service = Service(
        id=uuid4(),
        name=name,
        duration_minutes=duration_minutes,
        price=price,
        is_active=is_active,
    )
    return await repository.create(service)


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


async def assign_service_to_master(
    db_session,
    master_id,
    service_id,
) -> None:
    await db_session.execute(
        insert(master_services).values(
            master_id=master_id,
            service_id=service_id,
        )
    )
    await db_session.flush()


@pytest.mark.asyncio
async def test_create_service(db_session):
    repository = ServiceRepository(db_session)
    service = Service(
        id=uuid4(),
        name="Haircut",
        duration_minutes=60,
        price=500,
        description="Professional haircut.",
    )

    created_service = await repository.create(service)

    assert created_service == service


@pytest.mark.asyncio
async def test_get_service_by_id(db_session):
    repository = ServiceRepository(db_session)
    service = await create_test_service(repository)

    found_service = await repository.get_by_id(service.id)

    assert found_service == service


@pytest.mark.asyncio
async def test_get_service_by_id_returns_none_when_not_found(db_session):
    repository = ServiceRepository(db_session)

    found_service = await repository.get_by_id(uuid4())

    assert found_service is None


@pytest.mark.asyncio
async def test_get_all_services(db_session):
    repository = ServiceRepository(db_session)

    first_service = await create_test_service(
        repository,
        name="Haircut",
    )
    second_service = await create_test_service(
        repository,
        name="Manicure",
        duration_minutes=90,
        price=700,
    )

    services = await repository.get_all()

    assert len(services) == 2
    assert first_service in services
    assert second_service in services


@pytest.mark.asyncio
async def test_get_active_services(db_session):
    repository = ServiceRepository(db_session)

    active_service = await create_test_service(
        repository,
        name="Haircut",
    )
    await create_test_service(
        repository,
        name="Old service",
        is_active=False,
    )

    services = await repository.get_active()

    assert services == [active_service]


@pytest.mark.asyncio
async def test_get_services_by_master_id(db_session):
    repository = ServiceRepository(db_session)
    master = await create_test_master(db_session)
    service = await create_test_service(repository)

    await assign_service_to_master(
        db_session,
        master.id,
        service.id,
    )

    services = await repository.get_by_master_id(master.id)

    assert services == [service]


@pytest.mark.asyncio
async def test_get_active_services_by_master_id(db_session):
    repository = ServiceRepository(db_session)
    master = await create_test_master(db_session)

    active_service = await create_test_service(
        repository,
        name="Haircut",
    )
    await assign_service_to_master(
        db_session,
        master.id,
        active_service.id,
    )

    inactive_service = await create_test_service(
        repository,
        name="Old service",
        is_active=False,
    )
    await assign_service_to_master(
        db_session,
        master.id,
        inactive_service.id,
    )

    services = await repository.get_active_by_master_id(master.id)

    assert services == [active_service]


@pytest.mark.asyncio
async def test_update_service(db_session):
    repository = ServiceRepository(db_session)
    service = await create_test_service(repository)

    updated_service = Service(
        id=service.id,
        name="Updated haircut",
        duration_minutes=90,
        price=800,
        description="Updated description.",
        is_active=True,
    )

    result = await repository.update(updated_service)

    assert result == updated_service


@pytest.mark.asyncio
async def test_update_service_returns_none_when_not_found(db_session):
    repository = ServiceRepository(db_session)
    service = Service(
        id=uuid4(),
        name="Unknown service",
        duration_minutes=60,
        price=500,
    )

    result = await repository.update(service)

    assert result is None


@pytest.mark.asyncio
async def test_deactivate_service(db_session):
    repository = ServiceRepository(db_session)
    service = await create_test_service(repository)

    deactivated_service = await repository.deactivate(service.id)

    assert deactivated_service is not None
    assert deactivated_service.is_active is False


@pytest.mark.asyncio
async def test_deactivate_service_returns_none_when_not_found(db_session):
    repository = ServiceRepository(db_session)

    result = await repository.deactivate(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_exists_by_name(db_session):
    repository = ServiceRepository(db_session)
    await create_test_service(repository, name="Haircut")

    result = await repository.exists_by_name("Haircut")

    assert result is True


@pytest.mark.asyncio
async def test_exists_by_name_returns_false_when_not_found(db_session):
    repository = ServiceRepository(db_session)

    result = await repository.exists_by_name("Unknown service")

    assert result is False
