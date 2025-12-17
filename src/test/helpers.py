from datetime import datetime, timedelta, UTC
from fastapi.testclient import TestClient

from src.main import app
from src.database import get_db
from src.models import Book, BookCopy


PATRON_1 = {
    "first_name": "Степан",
    "last_name": "Степаненко",
    "email": "stepanchyk@test.com",
    "phone_number": "0991234567",
}

PATRON_2 = {
    "first_name": "Іванка",
    "last_name": "Іваненко",
    "email": "ivanochka@test.com",
    "phone_number": "0731234567",
}

BOOK_1 = {
    "title": "Licking Spider",
    "authors": ["Gale of Waterdeep"],
    "pages": 100,
    "publisher": "Lolth",
    "language": "Англійська",
    "year_published": 2023,
    "genres": ["Горрор"],
    "price": 300,
}

BOOK_BATCH_1 = {
    "title": "Never Gonna Give You Up",
    "authors": ["Rick Astley"],
    "year_published": 2024,
    "pages": 300,
    "publisher": "Test Publisher",
    "language": "Українська",
    "genres": ["Романтика"],
    "price": 700,
    "quantity": 2,
}

BOOK_BATCH_2 = {
    "title": "алан вейк фром алан вейк",
    "authors": ["алан вейк"],
    "year_published": 1990,
    "pages": 120,
    "publisher": "алан вейк",
    "language": "Українська",
    "genres": ["алан вейк"],
    "price": 100,
    "quantity": 1,
}


def override_get_db(db_session):
    def _get_db():
        yield db_session
    return _get_db


def create_client(db_session):
    app.dependency_overrides[get_db] = override_get_db(db_session)
    return TestClient(app)


def _merge(base: dict, overrides: dict) -> dict:
    data = dict(base)
    data.update(overrides)
    return data


def create_patron(client, template=PATRON_1, **overrides) -> int:
    params = _merge(template, overrides)
    resp = client.post("/patrons/", params=params)
    assert resp.status_code == 200, resp.text
    return resp.json()["patron_id"]


def create_book_batch(client, db_session, template=BOOK_BATCH_1, **overrides) -> int:
    params = _merge(template, overrides)
    resp = client.post("/books/batch", params=params)
    assert resp.status_code == 200, resp.text
    book = db_session.query(Book).filter_by(title=params["title"]).one()
    return book.book_id


def get_book_copy(db_session, book_id: int) -> BookCopy:
    return db_session.query(BookCopy).filter_by(book_id=book_id).first()


def iso_end_time_in(days: int) -> str:
    return (datetime.now(UTC) + timedelta(days=days)).isoformat()


def iso_end_time_ago(days: int) -> str:
    return (datetime.now(UTC) - timedelta(days=days)).isoformat()
