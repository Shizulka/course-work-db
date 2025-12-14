import datetime
from fastapi import HTTPException
from src.repositories.notification_repository import NotificationRepository
from src.models import Notification

class NotificationService:
    def __init__(self , repo :NotificationRepository):
        self.repo = repo

    def get_notification_list(self):
        notification = self.repo.get_all

        if not notification:
            return []
        return notification
    
    def create_notification(self,contents: str ,  patron_id: int) :
        

        new_notification=Notification(
            contents= contents , 
            patron_id= patron_id  
            )
    
        return self.repo.create(new_notification)