from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.schemas import BookCreateWithCopies, BookCreateWithCopies 
from src.database import get_db
from src.repositories.book_repository import BookRepository
from src.services.book_services import BookService
from src.schemas import BookResponse

router = APIRouter(prefix="/books", tags=["Books"])

def get_book_service(db: Session = Depends(get_db)) -> BookService:
    repo = BookRepository(db) 
    service = BookService(repo) 
    return service

@router.post("/batch", response_model=BookResponse)
def create_book_batch(book_data: BookCreateWithCopies, db: Session = Depends(get_db)):
    repo = BookRepository(db)
    service = BookService(db, repo) 
    
    return service.create_book_with_copies(book_data)
@router.get("/", response_model=List[BookResponse])
def get_all_books(db: Session = Depends(get_db)):
    from src.models import Book
    return db.query(Book).all()

@router.post("/")
def add_book(title: str, pages: int, publisher: str,  language: str, year_published: str , service: BookService = Depends(get_book_service)):
    return service.create_book(title=title, pages=pages , publisher=publisher, language=language , year_published=year_published)