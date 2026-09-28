"""FinanceRAG FastAPI application entrypoint."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import __version__
from app.api.router import api_router
from app.core.config import Settings, get_settings
from app.core.logging import setup_logging
from app.db.database import create_db_engine, create_session_factory


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create and dispose infrastructure clients.

    The async engine is created lazily (no connection is made until first
    use), so startup succeeds even when dependencies are unreachable;
    /api/health/ready reports their real status.
    """
    settings: Settings = app.state.settings
    engine = create_db_engine(settings)
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)
    try:
        yield
    finally:
        await engine.dispose()
        qdrant = getattr(app.state, "qdrant", None)
        if qdrant is not None:
            await qdrant.close()
        redis_integration = getattr(app.state, "redis", None)
        if redis_integration is not None:
            await redis_integration.close()


def create_app() -> FastAPI:
    """Build the FastAPI application."""
    settings = get_settings()
    setup_logging(settings)
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description=(
            "Self-hosted financial intelligence and document reasoning platform. "
            "Answers are designed to be evidence-grounded, verifiable and auditable."
        ),
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.include_router(api_router)
    return app


app = create_app()