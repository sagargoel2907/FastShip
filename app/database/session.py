from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel

from app.config import db_settings

engine = create_async_engine(
    url=db_settings.POSTGRES_URL, echo=True
)

async def create_db_and_tables():
    async with engine.begin() as connection:
        from app.database.models import Shipment, ShipmentEvent, Seller, ShipmentReview, ShipmentTag, Tag  # noqa: F401
        await connection.run_sync(SQLModel.metadata.create_all)
    
async def get_session():
    AsyncSessionLocal  = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        yield session
    