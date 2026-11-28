from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, time
from decimal import Decimal
from uuid import uuid4

import pytest

from master_booksy.domain.entities.appointment import Appointment
from master_booksy.domain.entities.client import Client
from master_booksy.domain.entities.master import Master
from master_booksy.domain.entities.schedule import Schedule
from master_booksy.domain.entities.service import Service
from master_booksy.domain.entities.time_off import TimeOff
from master_booksy.domain.entities.user import User
from master_booksy.domain.enums.appointment_status import AppointmentStatus
from master_booksy.domain.enums.user_role import UserRole


def test_user_creation() -> None:
    user = User(
        id=uuid4(),
        email="nattaya.srisai@example.com",
        password_hash="hashed_password",
        role=UserRole.CLIENT,
    )

    assert user.email == "nattaya.srisai@example.com"
    assert user.role == UserRole.CLIENT
    assert user.is_active is True


def test_client_and_master_creation() -> None:
    client = Client(
        id=uuid4(),
        user_id=uuid4(),
        full_name="Nattaya Srisai",
        phone="+66812345678",
    )
    master = Master(
        id=uuid4(),
        user_id=uuid4(),
        display_name="Arthit Chaiyaporn",
        bio="Senior Hair Stylist",
    )

    assert client.full_name == "Nattaya Srisai"
    assert master.display_name == "Arthit Chaiyaporn"


def test_service_creation() -> None:
    service = Service(
        id=uuid4(),
        name="Luxury Haircut & Styling",
        duration_minutes=60,
        price=120,
    )

    assert service.duration_minutes == 60
    assert service.price == 120


@pytest.mark.parametrize(
    ("duration", "price"),
    [
        (0, 120),
        (-30, 120),
        (60, -10),
    ],
)
def test_service_rejects_invalid_values(
    duration: int,
    price: int,
) -> None:
    with pytest.raises(ValueError):
        Service(
            id=uuid4(),
            name="Luxury Haircut & Styling",
            duration_minutes=duration,
            price=price,
        )


def test_schedule_creation() -> None:
    schedule = Schedule(
        id=uuid4(),
        master_id=uuid4(),
        weekday=0,
        opens_at=time(10, 0),
        closes_at=time(20, 0),
    )

    assert schedule.opens_at == time(10, 0)
    assert schedule.closes_at == time(20, 0)


@pytest.mark.parametrize(
    ("weekday", "opens_at", "closes_at"),
    [
        (-1, time(10, 0), time(20, 0)),
        (7, time(10, 0), time(20, 0)),
        (0, time(20, 0), time(10, 0)),
    ],
)
def test_schedule_rejects_invalid_values(
    weekday: int,
    opens_at: time,
    closes_at: time,
) -> None:
    with pytest.raises(ValueError):
        Schedule(
            id=uuid4(),
            master_id=uuid4(),
            weekday=weekday,
            opens_at=opens_at,
            closes_at=closes_at,
        )


def test_time_off_creation() -> None:
    time_off = TimeOff(
        id=uuid4(),
        master_id=uuid4(),
        starts_at=datetime(2026, 12, 1, 3, 0, tzinfo=UTC),
        ends_at=datetime(2026, 12, 1, 13, 0, tzinfo=UTC),
        reason="Annual leave",
    )

    assert time_off.reason == "Annual leave"


def test_time_off_rejects_invalid_period() -> None:
    with pytest.raises(ValueError):
        TimeOff(
            id=uuid4(),
            master_id=uuid4(),
            starts_at=datetime(2026, 12, 1, 13, 0, tzinfo=UTC),
            ends_at=datetime(2026, 12, 1, 3, 0, tzinfo=UTC),
        )


def test_appointment_creation() -> None:
    appointment = Appointment(
        id=uuid4(),
        client_id=uuid4(),
        master_id=uuid4(),
        service_id=uuid4(),
        starts_at=datetime(2026, 12, 2, 5, 0, tzinfo=UTC),
        ends_at=datetime(2026, 12, 2, 6, 0, tzinfo=UTC),
        status=AppointmentStatus.PENDING,
        price_at_booking=Decimal("120.00"),
    )

    assert appointment.status == AppointmentStatus.PENDING
    assert appointment.price_at_booking == Decimal("120.00")


def test_appointment_rejects_invalid_period() -> None:
    with pytest.raises(ValueError):
        Appointment(
            id=uuid4(),
            client_id=uuid4(),
            master_id=uuid4(),
            service_id=uuid4(),
            starts_at=datetime(2026, 12, 2, 6, 0, tzinfo=UTC),
            ends_at=datetime(2026, 12, 2, 5, 0, tzinfo=UTC),
        )


def test_domain_entities_are_immutable() -> None:
    user = User(
        id=uuid4(),
        email="nattaya.srisai@example.com",
        password_hash="hashed_password",
        role=UserRole.CLIENT,
    )

    with pytest.raises(FrozenInstanceError):
        setattr(user, "email", "new@example.com")  # noqa: B010
