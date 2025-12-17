import datetime
from fastapi import HTTPException
from src.repositories.notification_repository import NotificationRepository
from src.models import Notification, Patron

class NotificationService:
    def __init__(self , repo :NotificationRepository):
        self.repo = repo

    def get_notification_list(self, patron_id: int):
        patron_exists = self.repo.db.query(Patron).filter(Patron.patron_id == patron_id).first()

        if not patron_exists:
            raise HTTPException(status_code=404, detail="Patron not found")
        notifications = ( self.repo.db.query(Notification) .filter(Notification.patron_id == patron_id).all()
        )

        return notifications