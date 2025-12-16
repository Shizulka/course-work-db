import re
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from src.repositories.patron_repository import PatronRepository
from src.models import Patron, Notification
from src.templates import NotificationTemplates
from src.send_email_notification import send_email_notification


class PatronService:
    def __init__(self, repo: PatronRepository):
        self.repo = repo
        self.db = repo.db

    def get_patron_list(self):
        return self.repo.get_all() or []

    def update_patron(self, patron_id: int, updates: dict):
        patron = self.db.query(Patron).filter(Patron.patron_id == patron_id).first()

        if not patron:
            raise HTTPException(status_code=404, detail="Patron not found")

        for field, value in updates.items():
            setattr(patron, field, value)

        self.db.commit()
        self.db.refresh(patron)
        return patron

    def create_patron(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone_number: str
    ):
        email_pattern = r"^[A-Za-z0-9._+%-]+@[A-Za-z0-9.-]+\.[A-Za-z]+$"

        if len(phone_number) != 10:
            raise HTTPException(status_code=400, detail="Incorrect number format.")

        if not phone_number.isdigit():
            raise HTTPException(
                status_code=400,
                detail="The phone number must contain only numbers."
            )

        if not re.match(email_pattern, email):
            raise HTTPException(status_code=400, detail="Incorrect email format")

        try:
            with self.db.begin_nested():
                new_patron = Patron(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone_number=phone_number
                )
                self.db.add(new_patron)
                self.db.flush()

                message_body = NotificationTemplates.WELCOME

                notification = Notification(
                    patron_id=new_patron.patron_id,
                    contents=message_body
                )
                self.db.add(notification)

            if new_patron.email:
                send_email_notification(
                    to_email=new_patron.email,
                    subject="Welcome to the library!",
                    message=message_body
                )

            return {
                "message": "Patron successfully registered",
                "patron_id": new_patron.patron_id
            }

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="This patron already exists"
            )
