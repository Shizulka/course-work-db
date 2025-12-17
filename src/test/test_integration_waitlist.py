from src.models import Checkout
from src.test.helpers import create_client, create_patron, create_book_batch, get_book_copy, iso_end_time_in, PATRON_2

def test_add_to_waitlist_success(db_session):
    client = create_client(db_session)

    patron_id = create_patron(client)
    book_id = create_book_batch(client, db_session, quantity=0)

    resp = client.post(
        "/waitlist/",
        params={"book_id": book_id, "patron_id": patron_id},
    )

    assert resp.status_code == 200

def test_get_waitlist_position(db_session):
    client = create_client(db_session)

    patron1 = create_patron(client)
    patron2 = create_patron(client, template=PATRON_2)

    book_id = create_book_batch(client, db_session, quantity=0)

    client.post("/waitlist/", params={"book_id": book_id, "patron_id": patron1})
    client.post("/waitlist/", params={"book_id": book_id, "patron_id": patron2})

    resp = client.get(
        "/waitlist/position",
        params={"book_id": book_id, "patron_id": patron2},
    )

    assert resp.status_code == 200
    assert "1" in resp.json().get("message", "")

def test_issue_book_from_waitlist_manual(db_session):
    client = create_client(db_session)

    patron1 = create_patron(client)
    patron2 = create_patron(client, template=PATRON_2)

    book_id = create_book_batch(client, db_session, quantity=1)

    client.post(
        "/checkout/borrow",
        params={
            "book_id": book_id,
            "patron_id": patron1,
            "end_time": iso_end_time_in(3),
        },
    )

    client.post("/waitlist/", params={"book_id": book_id, "patron_id": patron2})

    checkout1 = (
        db_session.query(Checkout)
        .filter_by(patron_id=patron1)
        .one()
    )

    client.post(
        "/checkout/return",
        params={
            "patron_id": patron1,
            "book_copy_id": checkout1.book_copy_id,
        },
    )

    resp = client.post("/waitlist/issue", params={"book_id": book_id})
    assert resp.status_code == 200

    checkout2 = (
        db_session.query(Checkout)
        .filter_by(patron_id=patron2)
        .one()
    )

    assert checkout2 is not None
