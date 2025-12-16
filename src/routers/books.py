from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.schemas import  BookResponse
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

@router.post("/delete")
def delate_book(book_id:int, service: BookService = Depends(get_book_service)):
    return service.delate_book (book_id=book_id)

@router.post("/batch", response_model=BookResponse)
def create_book_batch( title: str,  authors: List[str] = Query(...), year_published: int = Query(...), pages: int = Query(...), publisher: str = Query(...),
    language: str = Query(...), genres: List[str] = Query(...), price: int = Query(...), quantity: int = Query(1), service: BookService = Depends(get_book_service)
):
    return service.create_book_with_copies( title=title,  authors=authors, year_published=year_published, pages=pages,
        publisher=publisher,language=language, genres=genres, price=price,quantity=quantity
    )

@router.patch("/{book_id}")
def update_book_route( book_id: int, title: Optional[str] = Query(None), pages: Optional[int] = Query(None), publisher: Optional[str] = Query(None),
    language: Optional[str] = Query(None),year_published: Optional[int] = Query(None),price: Optional[int] = Query(None),service: BookService = Depends(get_book_service)
):
    all_fields = {"title": title,"pages": pages, "publisher": publisher,"language": language,"year_published": year_published, "price": price }
    updates = {field_name: value for field_name, value in all_fields.items() if value is not None}

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    return service.update_book(book_id=book_id, updates=updates)
    
@router.post("/")
def add_book( title: str, authors: List[str] = Query(...), pages: int = Query(...), publisher: str = Query(...), language: str = Query(...), year_published: int = Query(...),
    genres: List[str] = Query(...), price: int = Query(...), service: BookService = Depends(get_book_service)
):
    return service.create_book(title=title, authors=authors, pages=pages, publisher=publisher,
        language=language, year_published=year_published, genres=genres,price=price
    )

@router.get("/", response_model=List[BookResponse])
def get_all_books(
    db: Session = Depends(get_db)
):
    from src.models import Book
    return db.query(Book).all()