from src.models import Notification
from src.repositories.ult_repository import UltRepository

class NotificationRepository(UltRepository):
    def __init__(self, db):
        super().__init__(db, Notification)
