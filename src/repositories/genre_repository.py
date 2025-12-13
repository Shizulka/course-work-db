from src.models import Genre
from src.repositories.ult_repository import UltRepository

class GenreRepository(UltRepository):
    def __init__(self, db):
        super().__init__(db, Genre)
