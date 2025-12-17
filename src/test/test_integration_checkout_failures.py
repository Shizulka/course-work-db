from src.models import Checkout
from src.test.helpers import create_client, create_patron, create_book_batch, get_book_copy, iso_end_time_in, PATRON_2

def test_borrow_fails_when_no_available_copies(db_session):
    client = create_client(db_session)

    patron_id = create_patron(client)
    book_id = create_book_batch(client, db_session, quantity=1)

    copy = get_book_copy(db_session, book_id)
    copy.available = 0
    db_session.flush()

    resp = client.post(
        "/checkout/borrow",
        params={
            "book_id": book_id,
            "patron_id": patron_id,
            "end_time": iso_end_time_in(7),
        },
    )

    assert resp.status_code == 409

def test_renew_fails_when_checkout_not_found(db_session):
    client = create_client(db_session)

    resp = client.put(
        "/checkout/renew",
        params={"checkout_id": 999999},
    )

    assert resp.status_code == 404

def test_renew_fails_when_waitlist_exists(db_session):
    client = create_client(db_session)

    patron1 = create_patron(client)
    patron2 = create_patron(client, template=PATRON_2)

    book_id = create_book_batch(client, db_session, quantity=1)

    client.post(
        "/checkout/borrow",
        params={
            "book_id": book_id,
            "patron_id": patron1,
            "end_time": iso_end_time_in(7),
        },
    )

    client.post(
        "/waitlist/",
        params={
            "book_id": book_id,
            "patron_id": patron2,
        },
    )

    checkout = (
        db_session.query(Checkout)
        .filter_by(patron_id=patron1)
        .one()
    )

    resp = client.put(
        "/checkout/renew",
        params={"checkout_id": checkout.checkout_id},
    )

    assert resp.status_code == 409

def test_return_fails_when_checkout_not_found(db_session):
    client = create_client(db_session)

    patron_id = create_patron(client)

    resp = client.post(
        "/checkout/return",
        params={
            "patron_id": patron_id,
            "book_copy_id": 9999,
        },
    )

    assert resp.status_code == 404

def test_borrow_fails_when_book_not_found(db_session):
    client = create_client(db_session)

    patron_id = create_patron(client)

    resp = client.post(
        "/checkout/borrow",
        params={
            "book_id": 9999,
            "patron_id": patron_id,
            "end_time": iso_end_time_in(7),
        },
    )

    assert resp.status_code == 404
