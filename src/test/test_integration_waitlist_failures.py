import pytest
from fastapi import HTTPException

from src.services.waitlist_services import WaitlistService
from src.repositories.waitlist_repository import WaitlistRepository
from src.repositories.copy_book_repository import BookCopyRepository

from src.test.helpers import create_client, create_patron, create_book_batch


def test_waitlist_fails_when_book_available(db_session):
    client = create_client(db_session)

    patron_id = create_patron(client)
    book_id = create_book_batch(client, db_session, quantity=1)

    resp = client.post(
        "/waitlist/",
        params={"book_id": book_id, "patron_id": patron_id},
    )

    assert resp.status_code == 400


def test_waitlist_duplicate_fails(db_session):
    client = create_client(db_session)

    patron_id = create_patron(client)
    book_id = create_book_batch(client, db_session, quantity=0)

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


def test_issue_book_from_waitlist_fails_when_empty(db_session):
    service = WaitlistService(
        repo=WaitlistRepository(db_session),
        book_copy_repo=BookCopyRepository(db_session),
    )

    with pytest.raises(HTTPException):
        service.issue_book_from_waitlist(book_id=999)
