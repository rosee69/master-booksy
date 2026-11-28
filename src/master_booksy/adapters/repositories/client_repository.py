from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from master_booksy.adapters.database.models.client_model import ClientModel
from master_booksy.adapters.repositories.base import BaseRepository
from master_booksy.domain.entities.client import Client


class ClientRepository(BaseRepository):
    """Repository for managing client profiles."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, client_id: UUID) -> Client | None:
        result = await self.session.execute(select(ClientModel).where(ClientModel.id == client_id))
        client_model = result.scalar_one_or_none()

        if client_model is None:
            return None

        return self._to_entity(client_model)

    async def get_by_user_id(self, user_id: UUID) -> Client | None:
        result = await self.session.execute(
            select(ClientModel).where(ClientModel.user_id == user_id)
        )
        client_model = result.scalar_one_or_none()

        if client_model is None:
            return None

        return self._to_entity(client_model)

    async def create(self, client: Client) -> Client:
        client_model = ClientModel(
            id=client.id,
            user_id=client.user_id,
            full_name=client.full_name,
            phone=client.phone,
        )

        self.session.add(client_model)
        await self.session.flush()

        return self._to_entity(client_model)

    @staticmethod
    def _to_entity(client_model: ClientModel) -> Client:
        return Client(
            id=client_model.id,
            user_id=client_model.user_id,
            full_name=client_model.full_name,
            phone=client_model.phone,
        )
