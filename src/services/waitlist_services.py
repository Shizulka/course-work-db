from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, UTC

from src.repositories.waitlist_repository import WaitlistRepository
from src.repositories.copy_book_repository import BookCopyRepository
from src.models import Book, Patron, Waitlist, Notification, Checkout, BookCopy 
from src.templates import NotificationTemplates
from src.send_email_notification import send_email_notification
import os

class WaitlistService:
    def __init__(self, repo: WaitlistRepository, book_copy_repo: BookCopyRepository):
        self.repo = repo
        self.book_copy_repo = book_copy_repo
        self.db: Session = repo.db

    def get_waitlist_list(self):
        waitlist = self.repo.get_all()
        return waitlist or []

    def get_patron_position(self, book_id: int, patron_id: int) -> int:
        item = self.repo.get_by_patron_and_book(patron_id, book_id)

        if not item:
            return 0

        my_time = item.created_at
        count = self.repo.count_ahead(book_id, my_time)
        return count + 1

    def create_waitlist(self, book_id: int, patron_id: int):
        inventory = self.book_copy_repo.get_by_book_id(book_id)

        if not inventory:
            raise HTTPException(
                status_code=404,
                detail="No inventory record for this book",
            )

        if inventory.available > 0:
            raise HTTPException(
                status_code=400,
                detail="Book is available! You can checkout directly instead of joining waitlist.",
            )

        try:
            new_waitlist = Waitlist(
                book_id=book_id,
                patron_id=patron_id,
            )
            self.db.add(new_waitlist)

            patron = (
                self.db.query(Patron)
                .filter(Patron.patron_id == patron_id)
                .first()
            )
            book = (
                self.db.query(Book)
                .filter(Book.book_id == book_id)
                .first()
            )

            if not patron:
                raise HTTPException(status_code=404, detail="Patron not found")

            if not book:
                raise HTTPException(status_code=404, detail="Book not found")

            message_body = NotificationTemplates.WAITLIST_ADDED.format(
                title=book.title
            )

            notification = Notification(
                patron_id=patron_id,
                contents=message_body,
            )
            self.db.add(notification)

            if patron.email and os.getenv("TESTING") != "1":
                send_email_notification(
                    to_email=patron.email,
                    subject="Library: Added to Waitlist",
                    message=message_body,
                )

            self.db.commit()
            self.db.refresh(new_waitlist)
            return new_waitlist

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Patron is already in waitlist for this book",
            )

        except HTTPException:
            self.db.rollback()
            raise

        except Exception:
            self.db.rollback()
            raise

    def issue_book_from_waitlist(self, book_id: int):
        waitlist_entry = (
            self.db.query(Waitlist)
            .filter(Waitlist.book_id == book_id)
            .order_by(Waitlist.created_at)
            .with_for_update()
            .first()
        )

        if not waitlist_entry:
            raise HTTPException(status_code=404, detail="Waitlist is empty")

        book_copy = (
            self.db.query(BookCopy)
            .filter(
                BookCopy.book_id == book_id,
                BookCopy.available > 0,
            )
            .with_for_update()
            .first()
        )

        if not book_copy:
            raise HTTPException(status_code=409, detail="No available copies")

        checkout = Checkout(
            patron_id=waitlist_entry.patron_id,
            book_copy_id=book_copy.book_copy_id,
            end_time=datetime.now(UTC),
            status="OK",
        )

        book_copy.available -= 1

        self.db.add(checkout)
        self.db.delete(waitlist_entry)
        self.db.commit()

        return checkout
