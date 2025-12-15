from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.repositories.copy_book_repository import BookCopyRepository
from src.services.copy_book_services import BookCopyService
from src.schemas import BookCopyResponse

router = APIRouter(prefix="/book copy", tags=["Book Copy"])


def get_copy_book_service(db: Session = Depends(get_db)) -> BookCopyService:
    repo =  BookCopyRepository(db) 
    service = BookCopyService(db, repo) 
    return service

@router.get("/", response_model=list[BookCopyResponse]) 
def get_all_copies(service: BookCopyService = Depends(get_copy_book_service)):
    return service.get_all()

@router.post("/update")
def add_copy_book( book_id: int , copy_number: int , service: BookCopyService = Depends(get_copy_book_service)):
    return service.update_available( book_id=book_id, copy_number= copy_number ) 

@router.post("/")
def add_copy_book( book_id: int , copy_number: int , available :int  , service: BookCopyService = Depends(get_copy_book_service)):
    return service.create_copy_book( book_id=book_id, copy_number= copy_number , available =available  ) 

