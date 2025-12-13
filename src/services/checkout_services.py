from fastapi import HTTPException
from models import Checkout
from repositories.checkout_repository import CheckoutRepository
from repositories.copy_book_repository import BookCopyRepository
from datetime import datetime , timedelta

class CheckoutService:
    def __init__(self, repo: CheckoutRepository, book_copy_repo: BookCopyRepository):
        self.repo = repo
        self.book_copy_repo = book_copy_repo

    def _update(self, checkout: Checkout):

        if not checkout.end_time:
            return

        now = datetime.now()

        if now > checkout.end_time:
            if checkout.status != "Overdue":
                checkout.status = "Overdue"
        
        elif checkout.end_time - now < timedelta(days=3):
            if checkout.status != "Soon":
                checkout.status = "Soon"
        
        else:
             if checkout.status != "OK":
                checkout.status = "OK"

    def get_checkout_list(self):
        checkout = self.repo.get_all

        if not checkout:
            return []
        return checkout
    
    
    
    def create_checkout(self, book_id: int, book_copy_id: int, patron_id: int, end_time: datetime):
        if not end_time:
            raise HTTPException(status_code=400, detail="End time is required")
        
        if end_time < datetime.now():
            raise HTTPException(status_code=400, detail="End time cannot be in the past")
        
        inventory_record = self.book_copy_repo.get_by_book_id(book_id)
        
        if not inventory_record:
            raise HTTPException(status_code=404, detail="Inventory record not found for this book")
        
        if inventory_record.available < 1:
             raise HTTPException(
                status_code=409, 
                detail="No books available. Join waitlist."
            )
        
        new_checkout = Checkout(
            book_copy_id=inventory_record.id, 
            patron_id=patron_id,
            end_time=end_time
        )

        inventory_record.available -= 1

        self.repo.create(new_checkout)
        
        return new_checkout