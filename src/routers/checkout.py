from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from src.schemas import CheckoutResponse
from src.repositories.notification_repository import NotificationRepository
from src.services.notification_services import NotificationService
from src.database import get_db
from src.repositories.checkout_repository import CheckoutRepository
from src.services.checkout_services import CheckoutService
from src.repositories.copy_book_repository import BookCopyRepository

router = APIRouter(prefix="/checkout", tags=["Checkout"])

def get_checkout_service(db: Session = Depends(get_db)) -> CheckoutService:
    repo = CheckoutRepository(db)
    book_copy_repo = BookCopyRepository(db) 
    notification_repo = NotificationRepository(db)
    notification_service = NotificationService(notification_repo)
    return CheckoutService(repo=repo, book_copy_repo=book_copy_repo, notification_service=notification_service)


@router.get("/")
def get_checkouts(service: CheckoutService = Depends(get_checkout_service)):
    return service.get_checkout_list()

@router.post("/", response_model=CheckoutResponse)
def add_checkout(book_id: int,  patron_id: int,   end_time: datetime,  service: CheckoutService = Depends(get_checkout_service)):
  return service.create_checkout( book_id=book_id, patron_id=patron_id, end_time=end_time)