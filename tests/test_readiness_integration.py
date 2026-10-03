"""Integration test: readiness endpoint against live infrastructure.

Run with Docker services up:
    pytest -m integration
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.integration


def test_readiness_reports_ready() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["checks"] == {"database": "ok", "redis": "ok", "qdrant": "ok"}
