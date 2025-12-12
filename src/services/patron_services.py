from fastapi import HTTPException
from src.repositories.patron_repositories import PatronRepositories
from src.models import Patron
import re

class PatronService:
    def __init__(self , repo : PatronRepositories):
        self.repo = repo

    def get_patron_list(self):
        patron = self.repo.get_all

        if not patron:
            return []
        return patron
    
    def create_patron(self, first_name: str, last_name: str, email: str, phone_number: str ) :
        email_pattern = "^[A-Za-z0-9._+%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$"

        if len(phone_number) != 10:
            raise HTTPException(status_code=400, detail="Не правильний формат номеру.")

        if not phone_number.isdigit():
             raise HTTPException(status_code=400, detail="Номер телефону має містити тільки цифри.")
        
        if not re.match(email_pattern, email):
            raise HTTPException(status_code=400, detail="Некоректний формат емейлу")

        new_patron = Patron(
            first_name=first_name, 
            last_name=last_name, 
            email=email, 
            phone_number=phone_number
        )
    
        return self.repo.create(new_patron)