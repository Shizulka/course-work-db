from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from src.repositories.patron_repository import PatronRepository
from src.models import Patron
from src.models import Patron, Notification
from src.templates import NotificationTemplates
from src.send_email_notification import send_email_notification
import re
class PatronService:
    def __init__(self , repo : PatronRepository):
        self.repo = repo
        self.db = repo.db

    def get_patron_list(self):
        patron = self.repo.get_all()
        return patron or []
        return self.repo.get_all() or []

    def create_patron(self, first_name: str, last_name: str, email: str, phone_number: str ) :
    def create_patron(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone_number: str
    ):
        email_pattern = "^[A-Za-z0-9._+%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$"

        if len(phone_number) != 10:
              raise HTTPException(status_code=400, detail="Incorrect number format.")

                    if not phone_number.isdigit():
                         raise HTTPException(status_code=400, detail="The phone number must contain only numbers.")

                    if not re.match(email_pattern, email):
                        raise HTTPException(status_code=400, detail="Incorrect email format")

                    new_patron = Patron(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        phone_number=phone_number
                    )

                    try:
                        self.db.add(new_patron)
                        self.db.commit()
                        self.db.refresh(new_patron)
                        return {
                            "message": "The patron has successfully added",
                            "patron": new_patron
                        }
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
                         raise HTTPException(status_code=400, detail="This patron already exists")
                        self.db.rollback()
                        raise HTTPException(400, "This patron already exists")