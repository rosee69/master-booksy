from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from master_booksy.adapters.database.base import Base
from master_booksy.adapters.database.models import (
    appointment_model,  # noqa: F401
    client_model,  # noqa: F401
    master_model,  # noqa: F401
    master_service_model,  # noqa: F401
    schedule_model,  # noqa: F401
    service_model,  # noqa: F401
    time_off_model,  # noqa: F401
    user_model,  # noqa: F401
)
from master_booksy.config import settings


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    if settings.test_database_url is None:
        raise RuntimeError("TEST_DATABASE_URL is not configured.")

    if "master_booksy_test" not in settings.test_database_url:
        raise RuntimeError(
            "Tests must use the dedicated master_booksy_test database."
        )

    engine = create_async_engine(
        settings.test_database_url,
        echo=False,
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(
    test_engine,
) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    async with test_engine.connect() as connection:
        transaction = await connection.begin()

        async with session_factory(bind=connection) as session:
            yield session

        await transaction.rollback()