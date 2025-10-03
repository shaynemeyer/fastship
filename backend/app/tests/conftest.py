from uuid import UUID
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from app.database.session import get_session
from app.main import app

engine = create_async_engine(url="sqlite+aiosqlite:///:memory:")
test_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session_override():
    async with test_session() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_and_teardown():
    print("🧪 starting tests...")

    app.dependency_overrides[get_session] = get_session_override

    async with engine.begin() as connection:
        from app.database.models import DeliveryPartner, Seller, Shipment  # noqa: F401

        await connection.run_sync(SQLModel.metadata.create_all)

    yield

    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)

    app.dependency_overrides.clear()

    print("✅ finished!")
