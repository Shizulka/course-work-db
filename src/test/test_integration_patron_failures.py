from src.test.helpers import create_client, create_patron, create_book_batch, PATRON_1, iso_end_time_in

def test_create_patron_fails_invalid_email(db_session):
    client = create_client(db_session)

    bad = dict(PATRON_1)
    bad["email"] = "бі муві скрипт"

    resp = client.post("/patrons/", params=bad)
    assert resp.status_code == 400

def test_create_patron_fails_invalid_phone_length(db_session):
    client = create_client(db_session)

    bad = dict(PATRON_1)
    bad["phone_number"] = "12345"

    resp = client.post("/patrons/", params=bad)
    assert resp.status_code == 400

def test_create_patron_fails_phone_not_digits(db_session):
    client = create_client(db_session)

    bad = dict(PATRON_1)
    bad["phone_number"] = "09912abcde"

    resp = client.post("/patrons/", params=bad)
    assert resp.status_code == 400

def test_create_patron_fails_duplicate_email(db_session):
    client = create_client(db_session)

    first = client.post("/patrons/", params=PATRON_1)
    assert first.status_code == 200

    second = client.post("/patrons/", params=PATRON_1)
    assert second.status_code == 400

def test_soft_delete_patron_fails_with_active_loans(db_session):
    client = create_client(db_session)

    patron_id = create_patron(client)
    book_id = create_book_batch(client, db_session)

    client.post(
        "/checkout/borrow",
        params={
            "book_id": book_id,
            "patron_id": patron_id,
            "end_time": iso_end_time_in(7),
        },
    )

    resp = client.post(
        "/patrons/soft_delete",
        params={"patron_id": patron_id},
    )

    assert resp.status_code == 400
    assert "active book loans" in resp.text.lower()

def test_activate_patron_fails_not_found(db_session):
    client = create_client(db_session)

    resp = client.post(
        "/patrons/activate",
        params={"patron_id": 999999},
    )

    assert resp.status_code == 404