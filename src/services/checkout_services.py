from fastapi import HTTPException
from datetime import datetime, timedelta, UTC

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

    def renew_book(self, checkout_id: int):
        try:
            checkout = (
                self.db.query(Checkout)
                .filter(Checkout.checkout_id == checkout_id)
                .with_for_update()
                .first()
            )

            if not checkout:
                raise HTTPException(404, "Checkout record not found")

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

            now = datetime.now(UTC)

            if checkout.end_time.tzinfo is None:
                checkout_end = checkout.end_time.replace(tzinfo=UTC)
            else:
                checkout_end = checkout.end_time

            if checkout_end < datetime.now(UTC):
                raise HTTPException(
                    status_code=400,
                    detail="Cannot renew: The book is overdue."
                )

            new_end_time = checkout.end_time + timedelta(days=7)
            checkout.end_time = new_end_time
            checkout.status = "OK"

            formatted_date = new_end_time.strftime("%d.%m.%Y")
            book_title = checkout.book_copy.book.title

            message_body = NotificationTemplates.RENEWED.format(
                title=book_title,
                date=formatted_date
            )

            self.db.add(Notification(
                patron_id=checkout.patron_id,
                contents=message_body
            ))

            patron = checkout.patron
            if patron and patron.email:
                send_email_notification(
                    to_email=patron.email,
                    subject="Library: Book Renewed",
                    message=message_body
                )

            self.db.commit()

            return {
                "message": message_body,
                "new_due_date": formatted_date,
            }

        except Exception:
            self.db.rollback()
            raise



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
            checkout = (
                self.db.query(Checkout)
                .filter(
                    Checkout.patron_id == patron_id,
                    Checkout.book_copy_id == book_copy_id,
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

            book_copy.available += 1
            self.db.delete(checkout)

            message_body = NotificationTemplates.RETURN.format(
                title=book_copy.book.title if book_copy.book else "Book"
            )

            self.db.add(Notification(
                patron_id=patron_id,
                contents=message_body
            ))

            self.db.commit()

            return {
                "message": message_body,
                "new_availability": book_copy.available,
            }

        except Exception:
            self.db.rollback()
            raise



    def create_checkout(self, book_id: int, patron_id: int, end_time: datetime):

        if not end_time:
            raise HTTPException(status_code=400, detail="End time is required")

        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=UTC)

        if end_time < datetime.now(UTC):
            raise HTTPException(status_code=400, detail="End time cannot be in the past")

        active_checkouts = (
            self.db.query(Checkout)
            .filter(Checkout.patron_id == patron_id)
            .all()
        )

        for checkout in active_checkouts:
            self._update_status(checkout)
            if checkout.status == "Overdue":
                raise HTTPException(
                    status_code=403,
                    detail="You cannot borrow new books until overdue items are returned."
                )

        try:
            inventory_record = (
                self.db.query(BookCopy)
                .filter(BookCopy.book_id == book_id)
                .with_for_update()
                .one_or_none()
            )

            if not inventory_record:
                raise HTTPException(404, "Inventory record not found")

            if inventory_record.available < 1:
                raise HTTPException(409, "No books available. Join waitlist.")

            inventory_record.available -= 1

            new_checkout = Checkout(
                book_copy_id=inventory_record.book_copy_id,
                patron_id=patron_id,
                end_time=end_time
            )
            self.db.add(new_checkout)

            book_title = (
                inventory_record.book.title
                if inventory_record.book
                else "the book"
            )

            message_body = NotificationTemplates.BORROW.format(
                formatted_date=end_time.strftime("%d.%m.%Y"),
                title=book_title
            )

            self.db.add(Notification(
                patron_id=patron_id,
                contents=message_body
            ))

            patron = self.db.query(Patron).filter_by(patron_id=patron_id).first()
            if patron and patron.email:
                send_email_notification(
                    to_email=patron.email,
                    subject="Library: Borrowed book",
                    message=message_body
                )

            self.db.commit()
            return new_checkout

        except Exception:
            self.db.rollback()
            raise

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

    def _update_status(self, checkout: Checkout) -> bool:

        if not checkout.end_time:
            return

        if checkout.end_time.tzinfo is None:
            checkout.end_time = checkout.end_time.replace(tzinfo=UTC)

        now = datetime.now(UTC)
        old_status = checkout.status       

        if now > checkout.end_time:
            new_status = "Overdue"
            template = NotificationTemplates.OVERDUE
            subject = "Library: Overdue book"
        elif checkout.end_time - now <= timedelta(days=3):
            new_status = "Soon"
            template = NotificationTemplates.SOON
            subject = "Library: Return reminder"
        else:
            new_status = "OK"
            template = None

        if new_status == old_status:
            return False

        checkout.status = new_status
        
        if template:
            notification = Notification(
                patron_id=checkout.patron_id,
                contents=template
            )
            self.db.add(notification)

            patron = checkout.patron
            if patron and patron.email:
                send_email_notification(
                    to_email=patron.email,
                    subject=subject,
                    message=template
                )

        return True

    def update_all_checkout_statuses(self):
        checkouts = self.db.query(Checkout).all()

        changed = False
        for checkout in checkouts:
            updated = self._update_status(checkout)
            if updated:
                changed = True

        if changed:
            self.db.commit()