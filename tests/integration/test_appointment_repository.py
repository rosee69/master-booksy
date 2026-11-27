from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest

from master_booksy.adapters.repositories.appointment_repository import (
    AppointmentRepository,
)
from master_booksy.adapters.repositories.client_repository import (
    ClientRepository,
)
from master_booksy.adapters.repositories.master_repository import (
    MasterRepository,
)
from master_booksy.adapters.repositories.service_repository import (
    ServiceRepository,
)
from master_booksy.adapters.repositories.user_repository import UserRepository
from master_booksy.domain.entities.appointment import Appointment
from master_booksy.domain.entities.client import Client
from master_booksy.domain.entities.master import Master
from master_booksy.domain.entities.service import Service
from master_booksy.domain.entities.user import User
from master_booksy.domain.enums.appointment_status import AppointmentStatus
from master_booksy.domain.enums.user_role import UserRole

BANGKOK_TZ = ZoneInfo("Asia/Bangkok")


async def create_test_data(db_session):
    user_repository = UserRepository(db_session)

    master_user = User(
        id=uuid4(),
        email="master@example.com",
        password_hash="hashed-password",
        role=UserRole.MASTER,
    )
    client_user = User(
        id=uuid4(),
        email="client@example.com",
        password_hash="hashed-password",
        role=UserRole.CLIENT,
    )

    await user_repository.create(master_user)
    await user_repository.create(client_user)

    master = await MasterRepository(db_session).create(
        Master(
            id=uuid4(),
            user_id=master_user.id,
            display_name="Mile Phakphum",
        )
    )
    client = await ClientRepository(db_session).create(
        Client(
            id=uuid4(),
            user_id=client_user.id,
            full_name="Nattaya Srisai",
        )
    )
    service = await ServiceRepository(db_session).create(
        Service(
            id=uuid4(),
            name="Haircut",
            duration_minutes=60,
            price=1200,
        )
    )

    return master, client, service


async def create_test_appointment(
    repository,
    master_id,
    client_id,
    service_id,
    starts_at=None,
    status=AppointmentStatus.PENDING,
):
    starts_at = starts_at or datetime(
        2026, 8, 10, 10, 0, tzinfo=BANGKOK_TZ
    )

    return await repository.create(
        Appointment(
            id=uuid4(),
            client_id=client_id,
            master_id=master_id,
            service_id=service_id,
            starts_at=starts_at,
            ends_at=datetime.fromtimestamp(
                starts_at.timestamp() + 3600,
                tz=BANGKOK_TZ,
            ),
            status=status,
            price_at_booking=1200,
        )
    )


@pytest.mark.asyncio
async def test_create_and_get_appointment(db_session):
    repository = AppointmentRepository(db_session)
    master, client, service = await create_test_data(db_session)

    appointment = await create_test_appointment(
        repository,
        master.id,
        client.id,
        service.id,
    )

    found = await repository.get_by_id(appointment.id)
    missing = await repository.get_by_id(uuid4())

    assert found == appointment
    assert missing is None
    assert appointment.status == AppointmentStatus.PENDING


@pytest.mark.asyncio
async def test_get_appointments_by_client_and_master(db_session):
    repository = AppointmentRepository(db_session)
    master, client, service = await create_test_data(db_session)

    first = await create_test_appointment(
        repository, master.id, client.id, service.id
    )
    second = await create_test_appointment(
        repository,
        master.id,
        client.id,
        service.id,
        starts_at=datetime(
            2026, 8, 10, 12, 0, tzinfo=BANGKOK_TZ
        ),
    )

    assert await repository.get_by_client_id(client.id) == [first, second]
    assert await repository.get_by_master_id(master.id) == [first, second]


@pytest.mark.asyncio
async def test_get_appointments_by_master_and_period(db_session):
    repository = AppointmentRepository(db_session)
    master, client, service = await create_test_data(db_session)

    appointment = await create_test_appointment(
        repository, master.id, client.id, service.id
    )

    result = await repository.get_by_master_and_period(
        master.id,
        datetime(2026, 8, 10, 10, 30, tzinfo=BANGKOK_TZ),
        datetime(2026, 8, 10, 11, 30, tzinfo=BANGKOK_TZ),
    )

    assert result == [appointment]


@pytest.mark.asyncio
async def test_get_overlapping_appointments(db_session):
    repository = AppointmentRepository(db_session)
    master, client, service = await create_test_data(db_session)

    appointment = await create_test_appointment(
        repository, master.id, client.id, service.id
    )
    await create_test_appointment(
        repository,
        master.id,
        client.id,
        service.id,
        status=AppointmentStatus.CANCELLED,
    )

    result = await repository.get_overlapping(
        master.id,
        datetime(2026, 8, 10, 10, 30, tzinfo=BANGKOK_TZ),
        datetime(2026, 8, 10, 11, 30, tzinfo=BANGKOK_TZ),
    )

    without_current = await repository.get_overlapping(
        master.id,
        datetime(2026, 8, 10, 10, 30, tzinfo=BANGKOK_TZ),
        datetime(2026, 8, 10, 11, 30, tzinfo=BANGKOK_TZ),
        exclude_appointment_id=appointment.id,
    )

    assert result == [appointment]
    assert without_current == []


@pytest.mark.asyncio
async def test_update_appointment(db_session):
    repository = AppointmentRepository(db_session)
    master, client, service = await create_test_data(db_session)

    appointment = await create_test_appointment(
        repository, master.id, client.id, service.id
    )

    updated = Appointment(
        id=appointment.id,
        client_id=client.id,
        master_id=master.id,
        service_id=service.id,
        starts_at=datetime(
            2026, 8, 10, 12, 0, tzinfo=BANGKOK_TZ
        ),
        ends_at=datetime(
            2026, 8, 10, 13, 0, tzinfo=BANGKOK_TZ
        ),
        status=AppointmentStatus.CONFIRMED,
        price_at_booking=1200,
    )

    result = await repository.update(updated)

    assert result == updated
    assert await repository.update(
        Appointment(
            id=uuid4(),
            client_id=client.id,
            master_id=master.id,
            service_id=service.id,
            starts_at=updated.starts_at,
            ends_at=updated.ends_at,
        )
    ) is None
