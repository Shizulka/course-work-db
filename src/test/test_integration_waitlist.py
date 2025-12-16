from fastapi.testclient import TestClient

from src.main import app
from src.database import get_db
from src.models import Book, Patron, BookCopy, Waitlist

def override_get_db(db_session):
    def _get_db():
        yield db_session
    return _get_db

def create_patron(client):
    resp = client.post(
        "/patrons/",
        params={
            "first_name": "Wait",
            "last_name": "Tester",
            "email": "wait@test.com",
            "phone_number": "0998887777",
        },
    )
    assert resp.status_code == 200
    return resp.json()["patron_id"]

def create_book_with_copies(db_session, available: int):
    book = Book(
        title="Hi Andriy",
        language="EN",
        publisher="Test",
        year_published=2024,
        pages=100,
        price=300,
    )
    db_session.add(book)
    db_session.commit()

    copy = BookCopy(
        book_id=book.book_id,
        copy_number=1,
        available=available,
    )
    db_session.add(copy)
    db_session.commit()

    return book.book_id

def test_waitlist_fails_when_book_available(db_session):
    app.dependency_overrides[get_db] = override_get_db(db_session)
    client = TestClient(app)

    patron_id = create_patron(client)
    book_id = create_book_with_copies(db_session, available=1)

    resp = client.post(
        "/waitlist/",
        params={"book_id": book_id, "patron_id": patron_id},
    )

    assert resp.status_code == 400
    assert "Book is available" in resp.text

def test_add_to_waitlist_success(db_session):
    app.dependency_overrides[get_db] = override_get_db(db_session)
    client = TestClient(app)

    patron_id = create_patron(client)
    book_id = create_book_with_copies(db_session, available=0)

    resp = client.post(
        "/waitlist/",
        params={"book_id": book_id, "patron_id": patron_id},
    )

    assert resp.status_code == 200

    waitlist = db_session.query(Waitlist).filter_by(
        book_id=book_id, patron_id=patron_id
    ).first()

    assert waitlist is not None

def test_waitlist_duplicate_fails(db_session):
    app.dependency_overrides[get_db] = override_get_db(db_session)
    client = TestClient(app)

    patron_id = create_patron(client)
    book_id = create_book_with_copies(db_session, available=0)

    first = client.post(
        "/waitlist/",
        params={"book_id": book_id, "patron_id": patron_id},
    )
    assert first.status_code == 200

    second = client.post(
        "/waitlist/",
        params={"book_id": book_id, "patron_id": patron_id},
    )

    assert second.status_code in (400, 409)

def test_get_waitlist_position(db_session):
    app.dependency_overrides[get_db] = override_get_db(db_session)
    client = TestClient(app)

    patron1 = create_patron(client)

    resp = client.post(
        "/patrons/",
        params={
            "first_name": "Second",
            "last_name": "Tester",
            "email": "wait2@test.com",
            "phone_number": "0991112222",
        },
    )
    assert resp.status_code == 200
    patron2 = resp.json()["patron_id"]

    book_id = create_book_with_copies(db_session, available=0)

    client.post("/waitlist/", params={"book_id": book_id, "patron_id": patron1})
    client.post("/waitlist/", params={"book_id": book_id, "patron_id": patron2})

    resp = client.get(
        "/waitlist/position",
        params={"book_id": book_id, "patron_id": patron2},
    )

    assert resp.status_code == 200
    assert "позиція" in resp.json()["message"]
