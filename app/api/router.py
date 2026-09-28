"""Top-level API router: mounts all route groups under /api."""

from fastapi import APIRouter

from app.api.routes import analysis, auth, documents, evidence, health, research

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(research.router, prefix="/research", tags=["research"])
# Evidence router defines both /api/evidence/{id} and
# /api/research/{id}/evidence, so it is mounted without a prefix.
api_router.include_router(evidence.router, tags=["evidence"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])