from src.models import Book
from src.repositories.ult_repository import UltRepository

class BookRepository(UltRepository):
    def __init__(self, db):
        super().__init__(db, Book)


 