from src.models import BookCopy
from src.repositories.ult_repository import UltRepository
from sqlalchemy.orm import joinedload

class BookCopyRepository(UltRepository):
    def __init__(self, db):
        super().__init__(db, BookCopy)

    def get_by_book_id(self, book_id: int):
        return self.db.query(BookCopy).filter(BookCopy.book_id == book_id).first()
    
    def get_all(self):
        return self.db.query(BookCopy).options(joinedload(BookCopy.book)).all()