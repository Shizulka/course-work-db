from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.main import app


def test_health_endpoint(monkeypatch, db_session: Session):
    from src.database import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200

    data = resp.json()
    assert data["status"] == "ok"

    app.dependency_overrides.clear()
