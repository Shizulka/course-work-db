import datetime

from sqlalchemy import func
from src.models import Waitlist
from repositories.ult_repository import UltRepository

class WaitlistRepository(UltRepository):
    def __init__(self, db):
        super().__init__(db, Waitlist)

    def count_ahead (self , book_id : int , patron_id : int , now: datetime ):
        return self.db.query(func.count(Waitlist.waitlist_id)).filter(
            Waitlist.book_id == book_id,
            Waitlist.created_at < now
        ).scalar()

    def get_by_patron_and_book(self, patron_id: int, book_id: int):
         return self.db.query(Waitlist).filter(
            Waitlist.book_id == book_id,
            Waitlist.patron_id == patron_id
        ).first()