from src.test.helpers import create_client, BOOK_1

def test_create_book_fails_negative_pages(db_session):
    client = create_client(db_session)

    bad = dict(BOOK_1)
    bad["pages"] = -10

    resp = client.post("/books/", params=bad)
    assert resp.status_code >= 400

def test_create_book_fails_duplicate_identity(db_session):
    client = create_client(db_session)

    first = client.post("/books/", params=BOOK_1)
    assert first.status_code == 200

    second = client.post("/books/", params=BOOK_1)
    assert second.status_code >= 400

def test_create_book_fails_missing_required_param(db_session):
    client = create_client(db_session)

    bad = dict(BOOK_1)
    bad.pop("price")

    resp = client.post("/books/", params=bad)
    assert resp.status_code == 422
