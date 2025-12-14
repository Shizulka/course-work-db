from fastapi import HTTPException
from datetime import datetime , timedelta

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models import Checkout
from src.models import BookCopy
from src.models import Notification
from src.repositories.checkout_repository import CheckoutRepository
from src.repositories.copy_book_repository import BookCopyRepository


class CheckoutService:
    def __init__(self, repo: CheckoutRepository, book_copy_repo: BookCopyRepository):
        self.repo = repo
        self.book_copy_repo = book_copy_repo
        self.db: Session = repo.db

    def create_checkout(self, book_id: int, patron_id: int, end_time: datetime):
        formatted_date = end_time.strftime("%d.%m.%Y")

        if not end_time:
            raise HTTPException(status_code=400, detail="End time is required")
        
        if end_time < datetime.now():
            raise HTTPException(status_code=400, detail="End time cannot be in the past")
        
        try:
            with self.db.begin():

                inventory_record = (
                    self.db.query(BookCopy)
                    .filter(BookCopy.book_id == book_id)
                    .with_for_update()
                    .one_or_none()
                )

                if not inventory_record:
                    raise HTTPException(404, "Inventory record not found for this book")

                if inventory_record.available < 1:
                    raise HTTPException(409, "No books available. Join waitlist.")

                inventory_record.available -= 1
        
                new_checkout = Checkout(
                    book_copy_id=inventory_record.book_copy_id,
                    patron_id=patron_id,
                    end_time=end_time
                )
                self.db.add(new_checkout)

                formatted_date = end_time.strftime("%d.%m.%Y")
                notification = Notification(
                    patron_id=patron_id,
                    contents=f"You have successfully borrowed the book. Please return it by {formatted_date}."
                )
                self.db.add(notification)
                return new_checkout
            
        except IntegrityError:
            raise HTTPException(400, "Checkout failed due to data integrity error")
        
    def get_checkout_list(self):
        checkouts = self.repo.get_all() 

        if not checkouts:
            return []

        for checkout in checkouts:
            self._update_status(checkout)

        self.db.commit()
        return checkouts
        
    def _update_status(self, checkout: Checkout):

        if not checkout.end_time:
            return

        now = datetime.now()
        old_status = checkout.status

        if now > checkout.end_time:
            checkout.status = "Overdue"
        elif checkout.end_time - now < timedelta(days=3):
            checkout.status = "Soon"
        else:
            checkout.status = "OK"