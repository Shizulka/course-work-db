from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from repositories.book_repository import BookRepository
from src.services.book_services import BookService

router = APIRouter(prefix="/books", tags=["Books"])

def get_book_service(db: Session = Depends(get_db)) -> BookService:
    repo = BookRepository(db) 
    service = BookService(repo) 
    return service

@router.post("/")
def add_book(title: str, pages: int, publisher: str,  language: str, year_published: str , service: BookService = Depends(get_book_service)):
    return service.create_book(title=title, pages=pages , publisher=publisher, language=language , year_published=year_published) 