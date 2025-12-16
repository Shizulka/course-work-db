from fastapi import HTTPException
from src.repositories.book_repository import BookRepository
from src.repositories.waitlist_repository import WaitlistRepository # <-- ДОДАНО
from src.repositories.copy_book_repository import BookCopyRepository
from src.repositories.author_repository import AuthorRepository
from src.repositories.genre_repository import GenreRepository
from src.repositories.relations_repository import RelationsRepository
from src.services.waitlist_services import WaitlistService # <-- ДОДАНО

from src.models import Book, Author, Genre, BookCopy
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


class BookService:
    def __init__(
        self,
        db: Session,
        repo: BookRepository,
        waitlist_repo: WaitlistRepository = None,
        book_copy_repo: BookCopyRepository = None,
        author_repo: AuthorRepository = None,
        genre_repo: GenreRepository = None,
        relations_repo: RelationsRepository = None
    ):
        self.db = db
        self.repo = repo
        self.author_repo = author_repo or AuthorRepository(db)
        self.genre_repo = genre_repo or GenreRepository(db)
        self.relations_repo = relations_repo or RelationsRepository(db)

        self.waitlist_repo = waitlist_repo or WaitlistRepository(db)
        self.book_copy_repo = book_copy_repo or BookCopyRepository(db)
        self.waitlist_service = WaitlistService(self.waitlist_repo, self.book_copy_repo)

    def add_new_inventory(self, book_id: int, quantity: int):

        book = self.repo.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found.")

        inventory = self.book_copy_repo.get_by_book_id(book_id)

        if inventory:
            inventory.copy_number += quantity
            inventory.available += quantity
            self.db.add(inventory)
        else:
            new_copy = BookCopy(
                book_id=book_id,
                copy_number=quantity,
                available=quantity
            )
            self.db.add(new_copy)

        self.db.commit()
        self.db.refresh(book)

        issued_count = 0

        for _ in range(quantity):
            try:
                self.waitlist_service.issue_book_from_waitlist(book_id)
                issued_count += 1
            except HTTPException as e:
                if e.status_code == 404 or e.status_code == 409:
                    break
                raise
            except Exception:
                 self.db.rollback()
                 raise

        updated_inventory = self.book_copy_repo.get_by_book_id(book_id)
        remaining_available = updated_inventory.available if updated_inventory else 0

        return {
            "message": f"Successfully added {quantity} copies of '{book.title}'.",
            "issued_to_waitlist": issued_count,
            "remaining_available": remaining_available
        }
