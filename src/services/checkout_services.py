from fastapi import HTTPException
from datetime import datetime , timedelta

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models import Book, Checkout
from src.models import BookCopy
from src.models import Notification
from src.repositories.checkout_repository import CheckoutRepository
from src.repositories.copy_book_repository import BookCopyRepository


class CheckoutService:
    def init(self, repo: CheckoutRepository, book_copy_repo: BookCopyRepository):
        self.repo = repo
        self.book_copy_repo = book_copy_repo
        self.db: Session = repo.db


    def lost_book(self, patron_id: int, book_copy_id: int):
        checkout = self.db.query(Checkout).filter(
          Checkout.patron_id == patron_id,
          Checkout.book_copy_id == book_copy_id
        ).first()

        if not checkout:
            raise HTTPException(status_code=404, detail="No record of issuance found")

        book_copy = (
            self.db.query(BookCopy)
            .filter(BookCopy.book_copy_id == checkout.book_copy_id)
            .with_for_update()
            .first()
        )

        if not book_copy:
             raise HTTPException(status_code=404, detail="No copy of the book found in the database")

        book = self.db.query(Book).filter(
             Book.book_id == book_copy.book_id
        ).first()

        if not book:
             raise HTTPException(status_code=404, detail="Book not found")

        price = book_copy.book.price
        self.db.delete(checkout)
        self.db.commit()

        return {
             "message": f"Сума штрафу: {price:.2f} грн"
        }

    def return_book (self ,  patron_id :int , book_copy_id :int):
            checkout = self.db.query(Checkout).filter(
                 Checkout.patron_id == patron_id,
                 Checkout.book_copy_id == book_copy_id, 
                 ).first()

            if not checkout:
                raise HTTPException(status_code=404, detail="No record of issuance found")
            
            book_copy = self.db.query(BookCopy)\
                .filter(BookCopy.book_copy_id == checkout.book_copy_id)\
                .with_for_update()\
                .first()
            
            if not book_copy:
                raise HTTPException(status_code=404, detail="No copy of the book found in the database")
            
            book_copy.available += 1
            self.db.delete(checkout)
            self.db.commit()
            
            return {"message": "The book has been successfully returned.", "new_availability": book_copy.available}

    def create_checkout(self, book_id: int, patron_id: int, end_time: datetime):

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
        
    def get_checkout_list(self, patron_id: int, book_id: int | None = None):
        query = (
            self.db.query(Checkout)
            .filter(Checkout.patron_id == patron_id)
        )

        if book_id is not None:
            query = query.join(BookCopy).filter(BookCopy.book_id == book_id)

        checkouts = query.all()

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
