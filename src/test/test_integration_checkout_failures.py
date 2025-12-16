from datetime import datetime, timedelta, UTC
from fastapi.testclient import TestClient
from src.main import app
from src.database import get_db
from src.models import Book, BookCopy

def override_get_db(db_session):
    def _get_db():
        yield db_session
    return _get_db

def test_borrow_fails_when_no_available_copies(db_session):
    app.dependency_overrides[get_db] = override_get_db(db_session)
    client = TestClient(app)

    patron = client.post(
        "/patrons/",
        params={
            "first_name": "Степан",
            "last_name": "Степаненко",
            "email": "stepanchyk@test.com",
            "phone_number": "0991234567",
        },
    ).json()

    client.post(
        "/books/batch",
        params={
            "title": "the book",
            "authors": ["the author"],
            "year_published": 2024,
            "pages": 100,
            "publisher": "test",
            "language": "Українська",
            "genres": ["test"],
            "price": 100,
            "quantity": 1,
        },
    )

    book = db_session.query(Book).filter_by(title="the book").one()
    copy = db_session.query(BookCopy).filter_by(book_id=book.book_id).one()

    copy.available = 0
    db_session.flush()

    end_time = datetime.now(UTC) + timedelta(days=7)

    resp = client.post(
        "/checkout/borrow",
        params={
            "book_id": book.book_id,
            "patron_id": patron["patron_id"],
            "end_time": end_time.isoformat(),
        },
    )

    assert resp.status_code == 409
