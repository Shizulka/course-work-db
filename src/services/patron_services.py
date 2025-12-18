import re
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, UTC
from fastapi import HTTPException

from src.repositories.patron_repository import PatronRepository
from src.models import Patron, Notification ,Waitlist , Wishlist ,Checkout
from src.templates import NotificationTemplates
from src.send_email_notification import send_email_notification
from src.templates import NotificationTemplates

class PatronService:
    def __init__(self, repo: PatronRepository):
        self.repo = repo
        self.db = repo.db

    def get_patron_list(self):
        return self.repo.get_all() or []


    def hard_delete_patron(self):
        six_months_ago = datetime.now(UTC) - timedelta(minutes=2)

        patron = ( self.db.query(Patron).filter(Patron.status == "INACTIVE",Patron.inactivated_at <= six_months_ago).all())

        message_body = NotificationTemplates.GOODBYE_AFTER

        for patron in patron:
            if patron.email:
                try:
                    send_email_notification(
                        to_email=patron.email,
                        subject="Library Account Permanently Deleted",
                        message=NotificationTemplates.GOODBYE_AFTER
                    )
                except Exception as e:
                    print(f"Could not send email to {patron.email}: {e}")

            self.db.delete(patron)

        self.db.commit()

        return {"detail": f"Patrons has been deleted permanently"}


    def activate_patron (self, patron_id: int):
        patron = self.db.query(Patron).filter(Patron.patron_id == patron_id).first()

        if not patron:
            raise HTTPException(status_code=404, detail="Patron not found")

        if patron.status != "INACTIVE":
            raise HTTPException(status_code=404, detail="Patron is not inactive")

        patron.status = "ACTIVE"
        patron.inactivated_at = None

        message_body = NotificationTemplates.BACK

        self.db.add(Notification(
            patron_id=patron.patron_id,
            contents=message_body
        ))

        if patron.email:
            try:
                send_email_notification(
                    to_email=patron.email,
                    subject="Library Account activated",
                    message=message_body
                )
            except Exception as e:
                print(f"Could not send email: {e}")

        self.db.commit()
        self.db.refresh(patron)

        return {"detail": f"Patron  has been activated successfully"}


    def soft_delete_patron (self, patron_id: int):
        patron = self.db.query(Patron).filter(Patron.patron_id == patron_id).first()

        if not patron:
            raise HTTPException(status_code=404, detail="Patron not found")

        active_loans_count = (
            self.db.query(Checkout)
            .filter(Checkout.patron_id == patron_id)
            .count()
        )

        if active_loans_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot deactivate patron. They still have {active_loans_count} active book loans."
            )

        self.db.query(Waitlist).filter(Waitlist.patron_id == patron_id).delete()
        self.db.query(Wishlist).filter(Wishlist.patron_id == patron_id).delete()

        new_status = "INACTIVE"

        patron.status = new_status
        patron.inactivated_at = datetime.now(UTC)

        message_body = NotificationTemplates.GOODBYE

        self.db.add(Notification(
            patron_id=patron.patron_id,
            contents=message_body
        ))

        if patron.email:
            try:
                send_email_notification(
                    to_email=patron.email,
                    subject="Library Account Deactivated",
                    message=message_body
                )
            except Exception as e:
                print(f"Could not send email: {e}")

        self.db.commit()
        self.db.refresh(patron)

        return {"detail": f"Patron  has been deactivated successfully"}

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

            self.db.commit()
            self.db.refresh(new_patron)
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
