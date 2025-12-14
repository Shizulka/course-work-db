import datetime
from fastapi import HTTPException
from src.repositories.notification_repository import NotificationRepository
from src.models import Notification

class NotificationService:
    def __init__(self , repo :NotificationRepository):
        self.repo = repo

    def get_notification_list(self):
        return self.repo.get_all