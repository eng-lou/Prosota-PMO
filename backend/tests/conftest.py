from __future__ import annotations

import asyncio
import sys

import pytest

# psycopg3 requires SelectorEventLoop; Windows defaults to ProactorEventLoop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_db
from app.main import app
from app.models.base import Base
from app.models.organisation import Organisation
from app.models.period import Period
from app.models.project import Project

_ASYNC_URL = "postgresql+psycopg://postgres:password@localhost:5432/prosotapmo_test"
_SYNC_URL = "postgresql+psycopg://postgres:password@localhost:5432/prosotapmo_test"

_async_engine = create_async_engine(_ASYNC_URL)
_Session = async_sessionmaker(_async_engine, expire_on_commit=False)


# Sync fixture for schema setup — avoids pytest-asyncio event-loop scope issues
@pytest.fixture(scope="session", autouse=True)
def _schema():
    engine = create_engine(_SYNC_URL)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def _truncate():
    yield
    async with _Session() as session:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(text(f'TRUNCATE TABLE "{table.name}" CASCADE'))
        await session.commit()


@pytest_asyncio.fixture
async def db() -> AsyncSession:
    async with _Session() as session:
        yield session


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncClient:
    async def _override():
        yield db

    app.dependency_overrides[get_db] = _override
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def org(db: AsyncSession) -> Organisation:
    o = Organisation(name="Test Org", plan_tier="starter")
    db.add(o)
    await db.commit()
    await db.refresh(o)
    return o


@pytest_asyncio.fixture
async def project(db: AsyncSession, org: Organisation) -> Project:
    p = Project(org_id=org.id, name="Test Project", client_name="Test Client")
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@pytest_asyncio.fixture
async def live_period(db: AsyncSession, project: Project) -> Period:
    p = Period(project_id=project.id, period_label="Period 1", freeze_status="live")
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@pytest_asyncio.fixture
async def frozen_period(db: AsyncSession, project: Project) -> Period:
    p = Period(project_id=project.id, period_label="Period 0", freeze_status="frozen")
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p
