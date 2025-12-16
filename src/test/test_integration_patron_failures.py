from fastapi.testclient import TestClient
from src.main import app
from src.database import get_db

def override_get_db(db_session):
    def _get_db():
        yield db_session
    return _get_db


def test_create_patron_fails_invalid_email(db_session):
    app.dependency_overrides[get_db] = override_get_db(db_session)
    client = TestClient(app)

    resp = client.post(
        "/patrons/",
        params={
            "first_name": "Степан",
            "last_name": "Степаненко",
            "email": "бі муві скрипт",
            "phone_number": "0991234567",
        },
    )

    assert resp.status_code == 400

def test_create_patron_fails_invalid_phone_length(db_session):
    app.dependency_overrides[get_db] = override_get_db(db_session)
    client = TestClient(app)

    resp = client.post(
        "/patrons/",
        params={
            "first_name": "Степан",
            "last_name": "Степаненко",
            "email": "stepanchyk@test.com",
            "phone_number": "12345",
        },
    )

    assert resp.status_code == 400

def test_create_patron_fails_phone_not_digits(db_session):
    app.dependency_overrides[get_db] = override_get_db(db_session)
    client = TestClient(app)

    resp = client.post(
        "/patrons/",
        params={
            "first_name": "Степан",
            "last_name": "Степаненко",
            "email": "stepanchyk@test.com",
            "phone_number": "09912abcde",
        },
    )

    assert resp.status_code == 400

def test_create_patron_fails_duplicate_email(db_session):
    app.dependency_overrides[get_db] = override_get_db(db_session)
    client = TestClient(app)

    params = {
        "first_name": "Степан",
        "last_name": "Степаненко",
        "email": "stepanchyk@test.com",
        "phone_number": "0991234567",
    }

    first = client.post("/patrons/", params=params)
    assert first.status_code == 200

    second = client.post("/patrons/", params=params)
    assert second.status_code == 400
