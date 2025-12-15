from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from src.schemas import CheckoutResponse
from src.database import get_db
from src.repositories.checkout_repository import CheckoutRepository
from src.services.checkout_services import CheckoutService
from src.repositories.copy_book_repository import BookCopyRepository

router = APIRouter(prefix="/checkout", tags=["Checkout"])

def get_checkout_service(db: Session = Depends(get_db)) -> CheckoutService:
    repo = CheckoutRepository(db)
    book_copy_repo = BookCopyRepository(db) 
    return CheckoutService(repo=repo, book_copy_repo=book_copy_repo)

@router.post("/borrow", response_model=CheckoutResponse)
def borrow_book(book_id: int,  patron_id: int,   end_time: datetime,  service: CheckoutService = Depends(get_checkout_service)):
  return service.create_checkout( book_id=book_id, patron_id=patron_id, end_time=end_time)

@router.post("/return")
def return_book( patron_id :int , book_copy_id :int , service: CheckoutService = Depends(get_checkout_service)):
    return service.return_book(  patron_id=patron_id,  book_copy_id=book_copy_id)

@router.post("/lost_book")
def lost_book( patron_id :int , book_copy_id :int , service: CheckoutService = Depends(get_checkout_service)):
    return service.lost_book(  patron_id=patron_id,  book_copy_id=book_copy_id)

@router.get("/", response_model=list[CheckoutResponse])
def get_checkouts( patron_id: int,  book_id: int | None = None, service: CheckoutService = Depends(get_checkout_service),):
    return service.get_checkout_list(  patron_id=patron_id,  book_id=book_id)
