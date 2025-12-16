from datetime import datetime, timedelta, UTC
from fastapi.testclient import TestClient

from src.main import app
from src.database import get_db
from src.models import Patron, Book, BookCopy, Checkout

def override_get_db(db_session):
    def _get_db():
        yield db_session
    return _get_db

def test_checkout_borrow_book(db_session):
    app.dependency_overrides[get_db] = override_get_db(db_session)
    client = TestClient(app)

    patron_resp = client.post(
        "/patrons/",
        params={
            "first_name": "Степан",
            "last_name": "Степаненко",
            "email": "stepanchyk@test.com",
            "phone_number": "0991234567",
        },
    )
    assert patron_resp.status_code == 200
    patron_id = patron_resp.json()["patron_id"]

    book_resp = client.post(
        "/books/batch",
        params={
            "title": "Never Gonna You Up",
            "authors": ["Rick Ashley"],
            "year_published": 2024,
            "pages": 300,
            "publisher": "nwrhui",
            "language": "Українська",
            "genres": ["Романтика"],
            "price": 700,
            "quantity": 2,
        },
    )
    assert book_resp.status_code == 200

    book = (
        db_session.query(Book)
        .filter_by(title="Never Gonna You Up")
        .one()
    )

    book_copy = db_session.query(BookCopy).filter_by(book_id=book.book_id).first()
    assert book_copy.available == book_copy.copy_number

    end_time = datetime.now(UTC) + timedelta(days=14)

    borrow_resp = client.post(
        "/checkout/borrow",
        params={
            "book_id": book.book_id,
            "patron_id": patron_id,
            "end_time": end_time.isoformat(),
        },
    )

    assert borrow_resp.status_code == 200

    checkout = (
        db_session.query(Checkout)
        .filter_by(patron_id=patron_id)
        .one()
    )

    assert checkout.book_copy_id == book_copy.book_copy_id
    assert checkout.status in ("OK", "Soon", "Overdue")

    db_session.refresh(book_copy)
    assert book_copy.available == book_copy.copy_number - 1
