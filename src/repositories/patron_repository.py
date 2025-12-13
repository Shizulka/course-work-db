
from src.models import Patron
from src.repositories.ult_repository import UltRepository

class PatronRepository(UltRepository):
    def __init__(self, db):
        super().__init__(db, Patron)