from src.models import Patron
from src.test.helpers import create_client, create_patron, PATRON_1


def test_create_patron(db_session):
    client = create_client(db_session)

    patron_id = create_patron(client)

    patron = (
        db_session.query(Patron)
        .filter_by(email=PATRON_1["email"])
        .one()
    )

    assert patron.patron_id == patron_id
    assert patron.first_name == PATRON_1["first_name"]
    assert patron.last_name == PATRON_1["last_name"]
