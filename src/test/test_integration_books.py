from fastapi.testclient import TestClient

from src.main import app
from src.database import get_db
from src.models import Book, Author, Genre

def override_get_db(db_session):
    def _get_db():
        yield db_session
    return _get_db


def test_create_book_with_relations(db_session):
    app.dependency_overrides[get_db] = override_get_db(db_session)

    client = TestClient(app)

    resp = client.post(
        "/books/",
        params={
            "title": "Integration Testing Book",
            "authors": ["John Tester"],
            "pages": 250,
            "publisher": "Test Publisher",
            "language": "EN",
            "year_published": 2024,
            "genres": ["Testing"],
            "price": 500,
        },
    )

    assert resp.status_code == 200

    book = (
        db_session.query(Book)
        .filter_by(title="Integration Testing Book")
        .one()
    )

    assert book.language == "EN"
    assert book.pages == 250
    assert book.price == 500

    assert len(book.author) == 1
    assert book.author[0].name == "John Tester"

    assert len(book.genre) == 1
    assert book.genre[0].name == "Testing"

    author = db_session.query(Author).filter_by(name="John Tester").one()
    genre = db_session.query(Genre).filter_by(name="Testing").one()

    assert book in author.book
    assert book in genre.book
