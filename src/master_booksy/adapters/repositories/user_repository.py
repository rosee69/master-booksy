from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from master_booksy.adapters.database.models.user_model import UserModel
from master_booksy.adapters.repositories.base import BaseRepository
from master_booksy.domain.entities.user import User


class UserRepository(BaseRepository):
    """Repository for managing user accounts."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
        user_model = result.scalar_one_or_none()

        if user_model is None:
            return None

        return self._to_entity(user_model)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        user_model = result.scalar_one_or_none()

        if user_model is None:
            return None

        return self._to_entity(user_model)

    async def exists_by_email(self, email: str) -> bool:
        result = await self.session.execute(
            select(UserModel.id).where(UserModel.email == email).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def create(self, user: User) -> User:
        user_model = UserModel(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            role=user.role,
            is_active=user.is_active,
        )

        self.session.add(user_model)
        await self.session.flush()

        return self._to_entity(user_model)

    @staticmethod
    def _to_entity(user_model: UserModel) -> User:
        return User(
            id=user_model.id,
            email=user_model.email,
            password_hash=user_model.password_hash,
            role=user_model.role,
            is_active=user_model.is_active,
        )
