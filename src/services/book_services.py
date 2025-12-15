from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.schemas import BookCreateWithCopies
from src.repositories.book_repository import BookRepository
from src.models import Book, BookCopy, Author, Genre, Wishlist, Notification, Patron
from src.templates import NotificationTemplates
from src.send_email_notification import send_email_notification

class BookService:
    def __init__(self, db: Session, repo: BookRepository):
        self.db = db
        self.repo = repo

    def get_book_list(self):
        book = self.repo.get_all

        if not book:
            return []
        return book

    
    def fulfill_wishlist_for_book(self, book: Book):
        book_author_names = {a.name.lower() for a in book.author}

        wishlists = (
            self.db.query(Wishlist)
            .filter(
                Wishlist.title == book.title,
                Wishlist.language == book.language,
                Wishlist.publisher == book.publisher,
                Wishlist.year_published == book.year_published,
            )
            .all()
        )

        for w in wishlists:
            if w.author:
                wishlist_authors = {
                    a.strip().lower()
                    for a in w.author.split(",")
                    if a.strip()
                }

                if wishlist_authors.isdisjoint(book_author_names):
                    continue


            message = NotificationTemplates.WISHLIST_FULFILLED.format(
                title=book.title
            )

            self.db.add(Notification(
                patron_id=w.patron_id,
                contents=message
            ))

            patron = self.db.query(Patron).get(w.patron_id)
            if patron and patron.email:
                send_email_notification(
                    to_email=patron.email,
                    subject=f"Library: '{book.title}' is now available",
                    message=message
                )

            # заявка виконана
            self.db.delete(w)

    
    def create_book_with_copies(
        self,
        title: str,
        year_published: int,
        pages: int,
        publisher: str,
        language: str,
        price: int,
        quantity: int,
        authors: list[str],
        genres: list[str]
    ):
        if pages <= 0:
            raise HTTPException(400, "Pages must be > 0")
        if price < 0:
            raise HTTPException(400, "Price cannot be negative")
        if not authors:
            raise HTTPException(400, "At least one author required")
        if not genres:
            raise HTTPException(400, "At least one genre required")

        try:
            new_book = Book(
                title=title,
                year_published=year_published,
                pages=pages,
                publisher=publisher,
                language=language,
                price=price
            )
            self.db.add(new_book)
            self.db.flush()

            author_objs = []
            for name in authors:
                author = self.db.query(Author).filter_by(name=name).first()
                if not author:
                    author = Author(name=name)
                    self.db.add(author)
                    self.db.flush()
                author_objs.append(author)

            new_book.author = author_objs

            genre_objs = []
            for name in genres:
                genre = self.db.query(Genre).filter_by(name=name).first()
                if not genre:
                    genre = Genre(name=name)
                    self.db.add(genre)
                    self.db.flush()
                genre_objs.append(genre)

            new_book.genre = genre_objs

            copy = BookCopy(
                book_id=new_book.book_id,
                copy_number=quantity,
                available=quantity
            )
            self.db.add(copy)

            self.fulfill_wishlist_for_book(new_book)

            self.db.commit()
            self.db.refresh(new_book)
            return new_book

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(400, "This book already exists")


    def create_book(
        self,
        title: str,
        authors: list[str],
        pages: int,
        publisher: str,
        language: str,
        year_published: int,
        genres: list[str],
        price: int
    ):
        if pages <= 0:
            raise HTTPException(status_code=400, detail="There must be more than 0 pages")

        if price < 0:
            raise HTTPException(status_code=400, detail="Price cannot be negative")

        try:
            new_book = Book(
                title=title,
                publisher=publisher,
                language=language,
                year_published=year_published,
                pages=pages,
                price=price
            )
            self.db.add(new_book)
            self.db.flush()

            author_objs = []
            for name in authors:
                author = (
                    self.db.query(Author)
                    .filter(Author.name == name)
                    .first()
                )
                if not author:
                    author = Author(name=name)
                    self.db.add(author)
                    self.db.flush()

                author_objs.append(author)

            new_book.author = author_objs

            genre_objs = []
            for name in genres:
                genre = (
                    self.db.query(Genre)
                    .filter(Genre.name == name)
                    .first()
                )
                if not genre:
                    genre = Genre(name=name)
                    self.db.add(genre)
                    self.db.flush()

                genre_objs.append(genre)

            new_book.genre = genre_objs

            self.db.commit()
            self.db.refresh(new_book)
            return new_book

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="This book already exists")
