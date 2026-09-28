"""Create the initial organization and admin user.

Usage (inside the API container):
    docker compose exec api python scripts/seed.py

The password is taken from SEED_ADMIN_PASSWORD when set; otherwise a
random password is generated and printed once to stdout (never logged).
Idempotent: exits without changes if the admin user already exists.
"""

import asyncio
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.logging import setup_logging  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.db.database import create_db_engine, create_session_factory  # noqa: E402
from app.db.models import Organization, User, UserRole  # noqa: E402

DEFAULT_ORG_NAME = "Default Organization"


async def _seed(session: AsyncSession, email: str) -> bool:
    existing = (
        await session.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()
    if existing is not None:
        print(f"Admin user already exists: {email}")
        return False

    settings = get_settings()
    if settings.seed_admin_password is not None:
        password = settings.seed_admin_password.get_secret_value()
        generated = False
    else:
        password = secrets.token_urlsafe(16)
        generated = True

    organization = (
        await session.execute(select(Organization).where(Organization.name == DEFAULT_ORG_NAME))
    ).scalar_one_or_none()
    if organization is None:
        organization = Organization(name=DEFAULT_ORG_NAME)
        session.add(organization)
        await session.flush()

    session.add(
        User(
            organization_id=organization.id,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
            is_active=True,
        )
    )
    await session.commit()
    print(f"Created admin user: {email} (organization: {DEFAULT_ORG_NAME})")
    if generated:
        print(f"Generated password (shown once, not logged): {password}")
    return True


async def main() -> None:
    settings = get_settings()
    setup_logging(settings)
    engine = create_db_engine(settings)
    factory = create_session_factory(engine)
    try:
        async with factory() as session:
            await _seed(session, settings.seed_admin_email.lower())
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())