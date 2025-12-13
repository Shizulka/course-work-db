from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from src.database import get_db
from src.repositories.checkout_repository import CheckoutRepository
from src.services.checkout_services import CheckoutService
from src.repositories.copy_book_repository import BookCopyRepository

router = APIRouter(prefix="/checkout", tags=["Checkout"])

def get_checkout_service(db: Session = Depends(get_db)) -> CheckoutService:
    repo = CheckoutRepository(db)
    book_copy_repo = BookCopyRepository(db) 
    service = CheckoutService(repo, book_copy_repo) 
    
    return service


@router.get("/")
def get_checkouts(service: CheckoutService = Depends(get_checkout_service)):
    return service.get_checkout_list()

@router.post("/")
def add_checkout(book_id: int,  patron_id: int,   end_time: datetime,  service: CheckoutService = Depends(get_checkout_service)):
  return service.create_checkout( book_id=book_id, patron_id=patron_id, end_time=end_time)