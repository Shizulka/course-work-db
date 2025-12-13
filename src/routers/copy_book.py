from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from repositories.copy_book_repository import BookCopyRepository
from src.services.copy_book_services import BookCopyService

router = APIRouter(prefix="/book copy", tags=["Book Copy"])


def get_patron_service(db: Session = Depends(get_db)) -> BookCopyService:
    repo =  BookCopyRepository(db) 
    service = BookCopyService(repo) 
    return service

@router.post("/")
def add_copy_book( book_id: int , copy_number: int , available :int  , service: BookCopyService = Depends(get_patron_service)):
    return service.create_copy_book( book_id=book_id, copy_number= copy_number , available =available  ) 

