from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from typing import Sequence, TypeVar, Generic

ModelT = TypeVar('ModelT', bound=SQLModel)

class BaseService(Generic[ModelT]):
    def __init__(self, session: AsyncSession, model: type[ModelT]):
        self.session = session
        self.model = model
    
    async def _get(self, id: UUID) -> ModelT | None:
        return await self.session.get(self.model, id)

    async def _create(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def _update(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def _delete(self, id: UUID) -> None:
        await self.session.delete(await self._get(id))
        await self.session.commit()

    async def _get_all(self) -> Sequence[ModelT]:
        result = await self.session.scalars(select(self.model))
        return result.all()