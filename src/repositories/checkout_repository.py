from src.models import Checkout
from src.repositories.ult_repository import UltRepository
from sqlalchemy.orm import Session
from sqlalchemy import or_

class CheckoutRepository(UltRepository):
    def __init__(self, db: Session):
        super().__init__(db, Checkout)

    def get_active_checkouts_by_patron(self, patron_id: int):

        return self.db.query(Checkout).filter(
            Checkout.patron_id == patron_id,
            or_(
                Checkout.status == 'OK',
                Checkout.status == 'Soon',
                Checkout.status == 'Overdue'
            )
        ).all()

    def has_active_checkouts(self, patron_id: int) -> bool:
        return bool(self.db.query(Checkout.checkout_id).filter(
            Checkout.patron_id == patron_id,
            or_(
                Checkout.status == 'OK',
                Checkout.status == 'Soon',
                Checkout.status == 'Overdue'
            )
        ).first())
