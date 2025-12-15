from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from src.repositories.waitlist_repository import WaitlistRepository
from src.repositories.copy_book_repository import BookCopyRepository
from src.models import Waitlist, Notification, Checkout, BookCopy 

class WaitlistService:
    def __init__(self , repo : WaitlistRepository , book_copy_repo: BookCopyRepository):
        self.repo = repo
        self.book_copy_repo = book_copy_repo
        self.db: Session = repo.db

    def get_waitlist_list(self):
        waitlist = self.repo.get_all()
        
        if not waitlist:
            return []
        return waitlist
    
    def get_patron_position(self , book_id : int , patron_id : int )-> int:
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
                detail="No inventory record for this book"
            )

        if inventory.available > 0:
            raise HTTPException(
                status_code=400,
                detail="Book is available! You can checkout directly instead of joining waitlist."
            )

        try:
            new_waitlist = Waitlist(
                book_id=book_id,
                patron_id=patron_id
            )
            self.db.add(new_waitlist)

            notification = Notification(
                patron_id=patron_id,
                contents="You have been added to the waitlist for this book."
            )
            self.db.add(notification)

            self.db.commit()
            self.db.refresh(new_waitlist)
            return new_waitlist

        except Exception:
            self.db.rollback()
            raise

    def issue_book_from_waitlist(self, book_id: int):
        try:
            with self.db.begin():

                inventory = (
                    self.db.query(BookCopy)
                    .filter(BookCopy.book_id == book_id)
                    .with_for_update()
                    .one_or_none()
                )

                if not inventory or inventory.available < 1:
                    raise HTTPException(
                        status_code=409,
                        detail="No available copies of this book"
                    )

                first_waiter = (
                    self.db.query(Waitlist)
                    .filter(Waitlist.book_id == book_id)
                    .order_by(Waitlist.created_at)
                    .with_for_update()
                    .first()
                )

                if not first_waiter:
                    raise HTTPException(
                        status_code=404,
                        detail="Waitlist is empty"
                    )

                checkout = Checkout(
                    patron_id=first_waiter.patron_id,
                    book_copy_id=inventory.book_copy_id,
                    end_time=datetime.now()
                )
                self.db.add(checkout)

                inventory.available -= 1

                self.db.delete(first_waiter)

                notification = Notification(
                    patron_id=first_waiter.patron_id,
                    contents=(
                        "The book you were waiting for is now available. "
                        "Please visit the library to collect it."
                    )
                )
                self.db.add(notification)

                return checkout

        except Exception:
            self.db.rollback()
            raise
