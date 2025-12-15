from fastapi import HTTPException
from datetime import datetime , timedelta

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models import Checkout, Patron, Waitlist
from src.models import Book
from src.models import BookCopy
from src.models import Notification
from src.repositories.checkout_repository import CheckoutRepository
from src.repositories.copy_book_repository import BookCopyRepository
from src.templates import NotificationTemplates
from src.send_email_notification import send_email_notification

class CheckoutService:
    def __init__(self, repo: CheckoutRepository, book_copy_repo: BookCopyRepository):
        self.repo = repo
        self.book_copy_repo = book_copy_repo
        self.db: Session = repo.db

    def renew_book(self, checkout_id : int):
        try:
            with self.db.begin():
                checkout = (
                    self.db.query(Checkout)
                    .filter(Checkout.checkout_id == checkout_id)
                    .with_for_update()
                    .first()
                )

                if not checkout:
                    raise HTTPException(status_code=404, detail="Checkout record not found")
                
                book_id = checkout.book_copy.book_id
                waitlist_count = (
                    self.db.query(Waitlist)
                    .filter(Waitlist.book_id == book_id)
                    .count()
                )

                if waitlist_count > 0:
                    raise HTTPException(
                        status_code=409, 
                        detail="Cannot renew: Other patrons are waiting for this book."
                    )
                
                if checkout.end_time < datetime.now():
                    raise HTTPException(
                        status_code=400,
                        detail="Cannot renew: The book is overdue. Please return it and pay the fine."
                    )
                
                new_end_time = checkout.end_time + timedelta(days=7)

                checkout.end_time = new_end_time
                checkout.status = "OK"
            
                formatted_date = new_end_time.strftime("%d.%m.%Y")
                message_body = NotificationTemplates.RENEWED.format(date=formatted_date)

                notification = Notification(
                    patron_id=checkout.patron_id,
                    contents=message_body
                )
                self.db.add(notification)

                patron = checkout.patron 
                if patron and patron.email:
                    send_email_notification(
                        to_email=patron.email,
                        subject="Library: Book Renewed",
                        message=message_body
                    )

                return {"message": message_body, "new_due_date": formatted_date}

        except Exception as e:
            self.db.rollback()
            raise e


    def lost_book(self, patron_id: int, book_copy_id: int):
        try:
            with self.db.begin():

                checkout = (
                    self.db.query(Checkout)
                    .filter(
                        Checkout.patron_id == patron_id,
                        Checkout.book_copy_id == book_copy_id
                    )
                    .with_for_update()
                    .first()
                )

                if not checkout:
                    raise HTTPException(404, "No record of issuance found")

                book_copy = (
                    self.db.query(BookCopy)
                    .filter(BookCopy.book_copy_id == checkout.book_copy_id)
                    .with_for_update()
                    .first()
                )

                if not book_copy:
                    raise HTTPException(404, "No copy of the book found")

                book = (
                    self.db.query(Book)
                    .filter(Book.book_id == book_copy.book_id)
                    .first()
                )

                if not book:
                    raise HTTPException(404, "Book not found")

                book_copy.copy_number -= 1

                price = book.price
                self.db.delete(checkout)

                message_body = NotificationTemplates.FINE.format(price=price)
                
                notification = Notification(
                    patron_id=patron_id,
                    contents=message_body
                )
                self.db.add(notification)

                patron = self.db.query(Patron).filter(Patron.patron_id == patron_id).first()
                
                if patron and patron.email:
                    send_email_notification(
                        to_email=patron.email,
                        subject=f"Library: Fine for lost book '{book.title}'",
                        message=message_body
                    )

                return {"message": message_body}

        except Exception:
            self.db.rollback()
            raise

    def return_book(self, patron_id: int, book_copy_id: int):
        try:
            with self.db.begin():

                checkout = (
                    self.db.query(Checkout)
                    .filter(
                        Checkout.patron_id == patron_id,
                        Checkout.book_copy_id == book_copy_id
                    )
                    .with_for_update()
                    .first()
                )

                if not checkout:
                    raise HTTPException(
                        status_code=404,
                        detail="No record of issuance found"
                    )

                book_copy = (
                    self.db.query(BookCopy)
                    .filter(BookCopy.book_copy_id == checkout.book_copy_id)
                    .with_for_update()
                    .first()
                )

                if not book_copy:
                    raise HTTPException(
                        status_code=404,
                        detail="No copy of the book found in the database"
                    )

                book_copy.available += 1

                self.db.delete(checkout)

                message_body = NotificationTemplates.RETUTN

                patron = self.db.query(Patron).filter(Patron.patron_id == patron_id).first()
                
                book_title = book_copy.book.title if book_copy.book else "Book"

                if patron and patron.email:
                    send_email_notification(
                        to_email=patron.email,
                        subject=f"Library: Return Successful - {book_title}",
                        message=message_body
                    )

                return {
                    "message": message_body,
                    "new_availability": book_copy.available
                }

        except Exception:
            self.db.rollback()
            raise


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
                message_body = NotificationTemplates.BORROW.format(
                    formatted_date=formatted_date
                )
                notification = Notification(
                    patron_id=patron_id,
                    contents=message_body
                )
                self.db.add(notification)

                patron = self.db.query(Patron).filter(Patron.patron_id == patron_id).first()
            
                book_title = inventory_record.book.title if inventory_record.book else "Library Book"

                if patron and patron.email:
                    send_email_notification(
                        to_email=patron.email,
                        subject=f"Library: Borrowed '{book_title}'",
                        message=message_body
                    )

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
        new_status = old_status       

        if now > checkout.end_time:
            checkout.status = "Overdue"
        elif checkout.end_time - now < timedelta(days=3):
            checkout.status = "Soon"
        else:
            checkout.status = "OK"

        if old_status != new_status:
            checkout.status = new_status
        
            template = None
            if new_status == "Soon":
                template = NotificationTemplates.SOON
            elif new_status == "Overdue":
                template = NotificationTemplates.OVERDUE
            
            if template:
                notification = Notification(
                    patron_id=checkout.patron_id,
                    contents=template
                )
                self.db.add(notification)

                patron = checkout.patron 
                
                book_title = "Library Book"
                if checkout.book_copy and checkout.book_copy.book:
                    book_title = checkout.book_copy.book.title

                if patron and patron.email:
                    send_email_notification(
                        to_email=patron.email,
                        subject=f"Library Notification: Status {new_status}",
                        message=template
                    )
