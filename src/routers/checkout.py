from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from src.database import get_db
from src.repositories.checkout_repositories import CheckoutRepositories
from src.services.checkout_services import CheckoutService

router = APIRouter(prefix="/checkout", tags=["Checkout"])

def get_checkout_service(db: Session = Depends(get_db)) -> CheckoutService:
    repo = CheckoutRepositories(db) 
    service = CheckoutService(repo) 
    return service

@router.get("/")
def get_checkouts(service: CheckoutService = Depends(get_checkout_service)):
    return service.get_checkout_list()

@router.post("/")
def add_checkout(book_copy_id: int,  patron_id: int,   end_time: datetime,  service: CheckoutService = Depends(get_checkout_service)):

    return service.create_checkout( book_copy_id=book_copy_id, patron_id=patron_id, end_time=end_time)