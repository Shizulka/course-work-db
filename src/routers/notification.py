from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.models import Notification
from src.database import get_db
from src.repositories.notification_repository import NotificationRepository
from src.services.notification_services import NotificationService
from src.schemas import NotificationResponse

router = APIRouter(prefix="/notification", tags=["Notification"])


def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    repo = NotificationRepository(db) 
    service = NotificationService(repo) 
    return service

@router.get("/{patron_id}", response_model=List[NotificationResponse])
def get_my_notifications(patron_id: int, db: Session = Depends(get_db)):
    repo = NotificationRepository(db)
    return db.query(Notification).filter(Notification.patron_id == patron_id).all()

@router.get("/", response_model=List[NotificationResponse])
def get_notification(service: NotificationService = Depends(get_notification_service)):
    return service.get_notification_list()