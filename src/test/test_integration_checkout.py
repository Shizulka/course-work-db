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
    assert checkout.status == "OK"
    assert checkout.end_time.date() == end_time.date()

    db_session.refresh(book_copy)
    assert book_copy.available == book_copy.copy_number - 1

def test_borrow_fails_when_end_time_in_past(db_session):
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
            "title": "Кицю, не їж шнурочки",
            "authors": ["Яндрута"],
            "year_published": 2025,
            "pages": 100,
            "publisher": "фцртцшгвф",
            "language": "Українська",
            "genres": ["уйлашщйу"],
            "price": 100,
            "quantity": 1,
        },
    )

    book = db_session.query(Book).filter_by(title="Кицю, не їж шнурочки").one()

    end_time = datetime.now(UTC) - timedelta(days=1)

    resp = client.post(
        "/checkout/borrow",
        params={
            "book_id": book.book_id,
            "patron_id": patron["patron_id"],
            "end_time": end_time.isoformat(),
        },
    )

    assert resp.status_code == 400
    assert "past" in resp.text.lower()

def test_checkout_status_soon(db_session):
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
            "title": "шцуоаоцу",
            "authors": ["ацйошйцу"],
            "year_published": 2024,
            "pages": 100,
            "publisher": "цфвцй",
            "language": "Українська",
            "genres": ["цйайшщцрщк3й"],
            "price": 100,
            "quantity": 1,
        },
    )

    book = db_session.query(Book).filter_by(title="шцуоаоцу").one()

    end_time = datetime.now(UTC) + timedelta(days=2)

    client.post(
        "/checkout/borrow",
        params={
            "book_id": book.book_id,
            "patron_id": patron["patron_id"],
            "end_time": end_time.isoformat(),
        },
    )

    resp = client.get(
        "/checkout/",
        params={"patron_id": patron["patron_id"]},
    )

    checkout = resp.json()[0]
    assert checkout["status"] == "Soon"

def test_checkout_return_book(db_session):
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
            "title": "wenfiewif",
            "authors": ["jnnfiuwqr"],
            "year_published": 1990,
            "pages": 120,
            "publisher": "ewfqgq",
            "language": "Українська",
            "genres": ["qwffwrgr"],
            "price": 100,
            "quantity": 1,
        },
    )

    book = db_session.query(Book).filter_by(title="wenfiewif").one()
    copy = db_session.query(BookCopy).filter_by(book_id=book.book_id).one()
    assert copy.available == 1

    end_time = datetime.now(UTC) + timedelta(days=7)
    borrow = client.post(
        "/checkout/borrow",
        params={
            "book_id": book.book_id,
            "patron_id": patron["patron_id"],
            "end_time": end_time.isoformat(),
        },
    )
    assert borrow.status_code == 200
    assert copy.available == 0

    checkout = (
        db_session.query(Checkout)
        .filter(Checkout.patron_id == patron["patron_id"])
        .one()
    )

    resp = client.post(
        "/checkout/return",
        params={
            "patron_id": patron["patron_id"],
            "book_copy_id": checkout.book_copy_id,
        },
    )

    assert resp.status_code == 200
    assert "return" in resp.json()["message"].lower()

    db_session.refresh(copy)
    assert copy.available == 1

    assert (
        db_session.query(Checkout)
        .filter(Checkout.patron_id == patron["patron_id"])
        .count()
    ) == 0


def test_checkout_renew_book(db_session):
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
            "title": "lqpokefimqeinf",
            "authors": ["wegwege"],
            "year_published": 2020,
            "pages": 150,
            "publisher": "wemgwueig",
            "language": "Українська",
            "genres": ["newuqfbiubqe"],
            "price": 100,
            "quantity": 1,
        },
    )

    book = db_session.query(Book).filter_by(title="lqpokefimqeinf").one()

    original_end = datetime.now(UTC) + timedelta(days=5)

    client.post(
        "/checkout/borrow",
        params={
            "book_id": book.book_id,
            "patron_id": patron["patron_id"],
            "end_time": original_end.isoformat(),
        },
    )

    checkout = (
        db_session.query(Checkout)
        .filter(Checkout.patron_id == patron["patron_id"])
        .one()
    )

    old_end = checkout.end_time

    resp = client.put(
        "/checkout/renew",
        params={"checkout_id": checkout.checkout_id},
    )

    assert resp.status_code == 200
    assert "loan period" in resp.json()["message"].lower()

    db_session.refresh(checkout)
    assert checkout.end_time > old_end
    assert checkout.status == "OK"
