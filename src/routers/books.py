from typing import List
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from src.schemas import BookCreateWithCopies, BookResponse
from src.database import get_db
from src.repositories.book_repository import BookRepository
from src.services.book_services import BookService

router = APIRouter(prefix="/books", tags=["Books"])

def get_book_service(
    db: Session = Depends(get_db)
) -> BookService:
    repo = BookRepository(db)
    service = BookService(db, repo)
    return service

@router.post("/batch", response_model=BookResponse)
def create_book_batch(
    title: str,
    authors: List[str] = Query(...),
    year_published: int = Query(...),
    pages: int = Query(...),
    publisher: str = Query(...),
    language: str = Query(...),
    genres: List[str] = Query(...),
    price: int = Query(...),
    quantity: int = Query(1),
    service: BookService = Depends(get_book_service)
):
    return service.create_book_with_copies(
        title=title,
        authors=authors,
        year_published=year_published,
        pages=pages,
        publisher=publisher,
        language=language,
        genres=genres,
        price=price,
        quantity=quantity
    )

@router.post("/")
def add_book(
    title: str,
    authors: List[str] = Query(...),
    pages: int = Query(...),
    publisher: str = Query(...),
    language: str = Query(...),
    year_published: int = Query(...),
    genres: List[str] = Query(...),
    price: int = Query(...),
    service: BookService = Depends(get_book_service)
):
    return service.create_book(
        title=title,
        authors=authors,
        pages=pages,
        publisher=publisher,
        language=language,
        year_published=year_published,
        genres=genres,
        price=price
    )

@router.get("/", response_model=List[BookResponse])
def get_all_books(
    db: Session = Depends(get_db)
):
    from src.models import Book
    return db.query(Book).all()

@router.post("/add-inventory/{book_id}")
def add_inventory(
    book_id: int = Path(..., description="ID of the book to add copies for"),
    quantity: int = Query(..., description="Number of new copies received"),
    service: BookService = Depends(get_book_service)
):

    return service.add_new_inventory(
        book_id=book_id,
        quantity=quantity
    )
