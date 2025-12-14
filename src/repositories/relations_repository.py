from sqlalchemy import func, insert, select
from sqlalchemy.orm import Session
from src.models import t_author_book, t_book_genres 

class RelationsRepository:
    def __init__(self, db: Session):
        self.db = db

    def count_authors_by_book(self, book_id: int) -> int:
        query = select(func.count()).select_from(t_author_book).where(t_author_book.c.book_id == book_id)
        return self.db.execute(query).scalar()

    def count_genres_by_book(self, book_id: int) -> int:
        query = select(func.count()).select_from(t_book_genres).where(t_book_genres.c.book_id == book_id)
        return self.db.execute(query).scalar()


    def add_author_to_book(self, book_id: int, author_id: int):
        stmt = insert(t_author_book).values(book_id=book_id, author_id=author_id)
        self.db.execute(stmt)
        return True

    def add_genre_to_book(self, book_id: int, genre_id: int):
        stmt = insert(t_book_genres).values(book_id=book_id, genre_id=genre_id)
        self.db.execute(stmt)
        return True