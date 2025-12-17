from src.models import Checkout
from src.test.helpers import create_client, create_patron, create_book_batch, get_book_copy, iso_end_time_in, iso_end_time_ago

def test_checkout_borrow_book(db_session):
    client = create_client(db_session)

    patron_id = create_patron(client)
    book_id = create_book_batch(client, db_session)

    copy = get_book_copy(db_session, book_id)
    assert copy.available == copy.copy_number

    end_time = iso_end_time_in(14)

    resp = client.post(
        "/checkout/borrow",
        params={
            "book_id": book_id,
            "patron_id": patron_id,
            "end_time": end_time,
        },
    )

    assert resp.status_code == 200

    checkout = (
        db_session.query(Checkout)
        .filter_by(patron_id=patron_id)
        .one()
    )

    assert checkout.book_copy_id == copy.book_copy_id
    assert checkout.status == "OK"

    db_session.refresh(copy)
    assert copy.available == copy.copy_number - 1

def test_borrow_fails_when_end_time_in_past(db_session):
    client = create_client(db_session)

    patron_id = create_patron(client)
    book_id = create_book_batch(client, db_session)

    resp = client.post(
        "/checkout/borrow",
        params={
            "book_id": book_id,
            "patron_id": patron_id,
            "end_time": iso_end_time_ago(1),
        },
    )

    assert resp.status_code == 400
    assert "past" in resp.text.lower()

def test_checkout_status_soon(db_session):
    client = create_client(db_session)

    patron_id = create_patron(client)
    book_id = create_book_batch(client, db_session, quantity=1)

    client.post(
        "/checkout/borrow",
        params={
            "book_id": book_id,
            "patron_id": patron_id,
            "end_time": iso_end_time_in(2),
        },
    )

    resp = client.get("/checkout/", params={"patron_id": patron_id})

    checkout = resp.json()[0]
    assert checkout["status"] == "Soon"

def test_checkout_return_book(db_session):
    client = create_client(db_session)

    patron_id = create_patron(client)
    book_id = create_book_batch(client, db_session, quantity=1)

    copy = get_book_copy(db_session, book_id)
    assert copy.available == 1

    client.post(
        "/checkout/borrow",
        params={
            "book_id": book_id,
            "patron_id": patron_id,
            "end_time": iso_end_time_in(7),
        },
    )

    assert copy.available == 0

    checkout = (
        db_session.query(Checkout)
        .filter_by(patron_id=patron_id)
        .one()
    )

    resp = client.post(
        "/checkout/return",
        params={
            "patron_id": patron_id,
            "book_copy_id": checkout.book_copy_id,
        },
    )

    assert resp.status_code == 200

    db_session.refresh(copy)
    assert copy.available == 1

    assert (
        db_session.query(Checkout)
        .filter_by(patron_id=patron_id)
        .count()
    ) == 0

def test_checkout_renew_book(db_session):
    client = create_client(db_session)

    patron_id = create_patron(client)
    book_id = create_book_batch(client, db_session, quantity=1)

    client.post(
        "/checkout/borrow",
        params={
            "book_id": book_id,
            "patron_id": patron_id,
            "end_time": iso_end_time_in(5),
        },
    )

    checkout = (
        db_session.query(Checkout)
        .filter_by(patron_id=patron_id)
        .one()
    )

    old_end = checkout.end_time

    resp = client.put(
        "/checkout/renew",
        params={"checkout_id": checkout.checkout_id},
    )

    assert resp.status_code == 200

    db_session.refresh(checkout)
    assert checkout.end_time > old_end
    assert checkout.status == "OK"
