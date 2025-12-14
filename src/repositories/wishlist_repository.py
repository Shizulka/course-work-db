from src.models import Wishlist
from src.repositories.ult_repository import UltRepository

class WishlistRepository(UltRepository):
    def __init__(self, db):
        super().__init__(db, Wishlist)