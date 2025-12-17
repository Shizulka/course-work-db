from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.models import Notification, Patron
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
def get_my_notifications( patron_id: int,db: Session = Depends(get_db)):
    patron = db.query(Patron).filter(Patron.patron_id == patron_id).first()
    if not patron:
        raise HTTPException(status_code=404, detail="Patron not found")

    return ( db.query(Notification) .filter(Notification.patron_id == patron_id) .all() )
