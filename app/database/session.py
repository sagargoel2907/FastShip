from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.config import settings

engine = create_async_engine(
    url=settings.POSTGRES_URL, echo=True
)

async def create_db_and_tables():
    async with engine.begin() as connection:
        from .models import Shipment  # noqa: F401
        await connection.run_sync(SQLModel.metadata.create_all)
    
async def get_session():
    AsyncSessionLocal  = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        yield session
    