import re
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from src.repositories.patron_repository import PatronRepository
from src.repositories.checkout_repository import CheckoutRepository # <-- ДОДАНО
from src.models import Patron, Notification
from src.templates import NotificationTemplates
from src.send_email_notification import send_email_notification
from sqlalchemy.orm import Session
from typing import Optional # <-- ДОДАНО

class PatronService:
    def __init__(self, repo: PatronRepository, db: Session): # <-- ЗМІНЕНО: ДОДАНО db
        self.repo = repo
        self.db = repo.db
        self.checkout_repo = CheckoutRepository(db) # <-- ДОДАНО ІНІЦІАЛІЗАЦІЮ

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

    # --- ДОДАНО НОВИЙ ФУНКЦІОНАЛ ---
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

        # 1. Перевірка активних видач
        has_active_books = self.checkout_repo.has_active_checkouts(patron_id)

        # 2. Перевірка та оновлення полів

        if has_active_books:
            # Заборона зміни імені та прізвища, якщо є активні видачі
            if first_name and first_name != patron.first_name:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot change first name while patron has active checkouts."
                )
            if last_name and last_name != patron.last_name:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot change last name while patron has active checkouts."
                )

        # Оновлення полів, якщо надані
        if first_name is not None:
             patron.first_name = first_name
        if last_name is not None:
             patron.last_name = last_name

        # Оновлення email з перевіркою формату
        if email and email != patron.email:
            email_pattern = r"^[A-Za-z0-9._+%-]+@[A-Za-z0-9.-]+\.[A-Za-z]+$"
            if not re.match(email_pattern, email):
                raise HTTPException(status_code=400, detail="Incorrect email format")
            patron.email = email

        # Оновлення phone_number з перевіркою формату
        if phone_number and phone_number != patron.phone_number:
            if len(phone_number) != 10 or not phone_number.isdigit():
                 raise HTTPException(status_code=400, detail="Incorrect phone number format (must be 10 digits).")
            patron.phone_number = phone_number

        # 4. Застосування змін
        try:
            self.db.add(patron)
            self.db.commit()
            self.db.refresh(patron)

            message = f"Patron data updated. Active checkouts: {has_active_books}."
            return {"message": message, "patron": patron}
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="This email or phone number is already in use.")
    # -------------------------------