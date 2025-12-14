from sqlite3 import IntegrityError
from fastapi import HTTPException
from src.repositories.patron_repository import PatronRepository
from src.models import Patron
import re

class PatronService:
    def __init__(self , repo : PatronRepository):
        self.repo = repo

    def get_patron_list(self):
        patron = self.repo.get_all

        if not patron:
            return []
        return patron
    
    def create_patron(self, first_name: str, last_name: str, email: str, phone_number: str ) :
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
             self.repo.create(new_patron)
             return {"message": "The patron has successfully added"}
        except IntegrityError:
             raise HTTPException(status_code=400, detail="This patron already exists")