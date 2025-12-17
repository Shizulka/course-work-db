from src.test.helpers import create_client, PATRON_1

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
