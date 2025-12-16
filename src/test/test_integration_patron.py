from fastapi.testclient import TestClient
from src.main import app
from src.database import get_db
from src.models import Patron

def override_get_db(db_session):
    def _get_db():
        yield db_session
    return _get_db


def test_create_patron(db_session):
    app.dependency_overrides[get_db] = override_get_db(db_session)

    client = TestClient(app)

    resp = client.post(
        "/patrons/",
        params={
            "first_name": "Степан",
            "last_name": "Степаненко",
            "email": "stepanchyk@test.com",
            "phone_number": "0991234567",
        },
    )

    assert resp.status_code == 200

    patron = (
        db_session.query(Patron)
        .filter_by(email="stepanchyk@test.com")
        .one()
    )

    assert patron.first_name == "Степан"
    assert patron.last_name == "Степаненко"
