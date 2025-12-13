from src.models import Checkout
from repositories.ult_repository import UltRepository

class CheckoutRepository(UltRepository):
    def __init__(self, db):
        super().__init__(db, Checkout)

    

