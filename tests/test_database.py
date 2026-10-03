"""Database session/model infrastructure tests.

Uses an in-memory SQLite database (StaticPool keeps one shared
connection), so no Docker or PostgreSQL is required.
"""

from collections.abc import AsyncIterator

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db import models
from app.db.database import Base


@pytest.fixture
async def session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        yield factory
    finally:
        await engine.dispose()


async def test_create_and_query_organization(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        session.add(models.Organization(name="Acme Corp"))
        await session.commit()
    async with session_factory() as session:
        organization = (await session.execute(select(models.Organization))).scalar_one()
        assert organization.name == "Acme Corp"
        assert organization.created_at is not None


async def test_session_rollback(session_factory: async_sessionmaker[AsyncSession]) -> None:
    async with session_factory() as session:
        session.add(models.Organization(name="Rollback Inc"))
        await session.rollback()
    async with session_factory() as session:
        organizations = (await session.execute(select(models.Organization))).scalars()
        assert list(organizations) == []


async def test_user_defaults(session_factory: async_sessionmaker[AsyncSession]) -> None:
    async with session_factory() as session:
        organization = models.Organization(name="Org")
        session.add(organization)
        await session.flush()
        session.add(
            models.User(
                organization_id=organization.id,
                email="user@example.com",
                password_hash="not-a-real-hash",
            )
        )
        await session.commit()
    async with session_factory() as session:
        user = (await session.execute(select(models.User))).scalar_one()
        assert user.role == models.UserRole.USER
        assert user.is_active is True
