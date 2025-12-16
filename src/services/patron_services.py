import re
from typing import Optional
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from src.repositories.patron_repository import PatronRepository
from src.models import Patron, Notification, Checkout
from src.templates import NotificationTemplates
from src.send_email_notification import send_email_notification


class PatronService:
    def __init__(self, repo: PatronRepository):
        self.repo = repo
        self.db = repo.db

    def get_patron_list(self):
        return self.repo.get_all() or []

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
            with self.db.begin():
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

    def update_patron(
        self,
        patron_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone_number: Optional[str] = None
    ):
        patron = self.repo.get_by_id(patron_id)
        if not patron:
            raise HTTPException(status_code=404, detail="Patron not found.")

        active_checkout = self.db.query(Checkout).filter(
            Checkout.patron_id == patron_id,
            Checkout.status.in_(["OK", "Soon", "Overdue"])
        ).first()

        if active_checkout:
            if (first_name and first_name != patron.first_name) or \
               (last_name and last_name != patron.last_name):
                raise HTTPException(
                    status_code=400,
                    detail="Cannot change name with active checkouts."
                )

        if email:
            email_pattern = r"^[A-Za-z0-9._+%-]+@[A-Za-z0-9.-]+\.[A-Za-z]+$"
            if not re.match(email_pattern, email):
                raise HTTPException(status_code=400, detail="Incorrect email format")
            patron.email = email

        if phone_number:
            if len(phone_number) != 10 or not phone_number.isdigit():
                raise HTTPException(status_code=400, detail="Incorrect phone number format")
            patron.phone_number = phone_number

        if first_name:
            patron.first_name = first_name
        if last_name:
            patron.last_name = last_name

        try:
            self.db.commit()
            return {"message": "Updated successfully", "patron_id": patron.patron_id}
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Email or phone already exists"
            )
