from src.models import Book, Author, Genre
from src.test.helpers import create_client, BOOK_1


def test_create_book_with_relations(db_session):
    client = create_client(db_session)

    resp = client.post("/books/", params=BOOK_1)
    assert resp.status_code == 200

    book = db_session.query(Book).filter_by(title=BOOK_1["title"]).one()

    assert book.pages == BOOK_1["pages"]
    assert book.language == BOOK_1["language"]
    assert book.price == BOOK_1["price"]

    assert len(book.author) == 1
    assert book.author[0].name == BOOK_1["authors"][0]

    assert len(book.genre) == 1
    assert book.genre[0].name == BOOK_1["genres"][0]

    author = db_session.query(Author).filter_by(name=BOOK_1["authors"][0]).one()
    genre = db_session.query(Genre).filter_by(name=BOOK_1["genres"][0]).one()

    assert book in author.book
    assert book in genre.book
