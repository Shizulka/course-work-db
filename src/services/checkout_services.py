from fastapi import HTTPException
from datetime import datetime , timedelta

from src.services.notification_services import NotificationService
from src.models import Checkout
from src.repositories.checkout_repository import CheckoutRepository
from src.repositories.copy_book_repository import BookCopyRepository


class CheckoutService:
    def __init__(self, repo: CheckoutRepository, book_copy_repo: BookCopyRepository, notification_service: NotificationService):
        self.repo = repo
        self.book_copy_repo = book_copy_repo
        self.notification_service = notification_service
        
    def _update(self, checkout: Checkout):

        if not checkout.end_time:
            return

        now = datetime.now()
        old_status = checkout.status

        if now > checkout.end_time:
            if checkout.status != "Overdue":
                checkout.status = "Overdue"
        
        elif checkout.end_time - now < timedelta(days=3):
            if checkout.status != "Soon":
                checkout.status = "Soon"
        
        else:
             if checkout.status != "OK":
                checkout.status = "OK"

        if old_status != checkout.status:
            
            if checkout.status == "Soon":
                msg = f"Reminder: The book must be returned in 3 days!"
                self.notification_service.create_notification(patron_id=checkout.patron_id, contents=msg)
            
            elif checkout.status == "Overdue":
                msg = f"ATTENTION: The book return deadline has passed! A fine will be charged."
                self.notification_service.create_notification(patron_id=checkout.patron_id, contents=msg)
                
    def get_checkout_list(self):
        checkouts = self.repo.get_all() 

        if not checkouts:
            return []

        for item in checkouts:
            self._update(item)
        self.repo.db.commit()

        return checkouts
    
    
    def create_checkout(self, book_id: int, patron_id: int, end_time: datetime):
        formatted_date = end_time.strftime("%d.%m.%Y")

        if not end_time:
            raise HTTPException(status_code=400, detail="End time is required")
        
        if end_time < datetime.now():
            raise HTTPException(status_code=400, detail="End time cannot be in the past")
        
        inventory_record = self.book_copy_repo.get_by_book_id(book_id)
        
        if not inventory_record:
            raise HTTPException(status_code=404, detail="Inventory record not found for this book")
        
        if inventory_record.available < 1:
             raise HTTPException(  status_code=409,   detail="No books available. Join waitlist.")
        
        new_checkout = Checkout(
            book_copy_id=inventory_record.book_copy_id,
            patron_id=patron_id,
            end_time=end_time
        )
        self.repo.create(new_checkout)
        inventory_record.available -= 1
        self.repo.db.commit()

        message = f"You have successfully borrowed the book. Please return it by {formatted_date}."
        self.notification_service.create_notification(patron_id=patron_id, contents=message)
        
        return new_checkout