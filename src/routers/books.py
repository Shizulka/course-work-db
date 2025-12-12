from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.repositories.book_repositories import BookRepositories
from src.services.book_services import BookService

router = APIRouter()

def get_book_service(db: Session = Depends(get_db)) -> BookService:
    repo = BookRepositories(db) 
    service = BookService(repo) 
    return service

@router.post("/books")
def add_book(title: str, pages: int, publisher: str,  language: str, year_published: str , service: BookService = Depends(get_book_service)):
    return service.create_book(title=title, pages=pages , publisher=publisher, language=language , year_published=year_published) 