from src.models import Author
from src.repositories.ult_repository import UltRepository

class AuthorRepository(UltRepository):
    def __init__(self, db):
        super().__init__(db, Author)


 