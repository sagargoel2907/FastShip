from httpx import ASGITransport, AsyncClient
import pytest_asyncio
from sqlmodel import SQLModel
from app.database.session import get_session
from app.main import app
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://test"
    ) as client:
        yield client


engine = create_async_engine(
    url="sqlite+aiosqlite:///:memory:"
)


async def get_session_override():
    AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)
    async with AsyncSessionLocal() as session:
        yield session


# test_id = "411ea652-829d-4f08-b816-612e6e2b410a"
# def get_id_override():
#     return test_id


@pytest_asyncio.fixture(autouse=True, scope="session")
async def setup_and_teardown():
    print("starting tests...")
    async with engine.begin() as connection:
        # from app.database.models import (
        #     Shipment,
        #     ShipmentEvent,
        #     Seller,
        #     ShipmentReview,
        #     ShipmentTag,
        #     Tag,
        # )  # noqa: F401

        await connection.run_sync(SQLModel.metadata.create_all)
    
    app.dependency_overrides[get_session] = get_session_override
    yield
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)
    app.dependency_overrides.clear()
    print("shutting down...")
