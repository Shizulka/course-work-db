from fastapi.testclient import TestClient
from src.main import app
from src.database import get_db

def override_get_db(db_session):
    def _get_db():
        yield db_session
    return _get_db


def test_create_book_fails_negative_pages(db_session):
    app.dependency_overrides[get_db] = override_get_db(db_session)
    client = TestClient(app)

    resp = client.post(
        "/books/",
        params={
            "title": "алан вейк фром алан вейк",
            "authors": ["алан вейк"],
            "pages": -10,
            "publisher": "алан вейк",
            "language": "Українська",
            "year_published": 2018,
            "genres": ["чемпіон оф зе лайт"],
            "price": 200,
        },
    )

    assert resp.status_code >= 400

def test_create_book_fails_duplicate_identity(db_session):
    app.dependency_overrides[get_db] = override_get_db(db_session)
    client = TestClient(app)

    params = {
        "title": "Licking Spider",
        "authors": ["Gale of Waterdeep"],
        "pages": 100,
        "publisher": "Lolth",
        "language": "Англійська",
        "year_published": 2023,
        "genres": ["Горрор"],
        "price": 300,
    }

    first = client.post("/books/", params=params)
    assert first.status_code == 200

    second = client.post("/books/", params=params)
    assert second.status_code >= 400

def test_create_book_fails_missing_required_param(db_session):
    app.dependency_overrides[get_db] = override_get_db(db_session)
    client = TestClient(app)

    resp = client.post(
        "/books/",
        params={
            "title": "Шахи для чайників",
            "authors": ["Підстаканник"],
            "pages": 100,
            "publisher": "Ложка",
            "language": "Українська",
            "year_published": 1984,
            "genres": ["Психологічний горрор"],
        },
    )

    assert resp.status_code == 422
