from typing import List,Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.database import get_db
from src.repositories.patron_repository import PatronRepository
from src.services.patron_services import PatronService

router = APIRouter(prefix="/patrons", tags=["Patrons"])


def get_patron_service(db: Session = Depends(get_db)) -> PatronService:
    repo = PatronRepository(db) 
    service = PatronService(repo) 
    return service

@router.post("/")
def add_patron(first_name: str, last_name: str, email: str, phone_number: str , service: PatronService = Depends(get_patron_service)):
    return service.create_patron(  first_name=first_name,  last_name=last_name,  email=email,  phone_number=phone_number) 

@router.patch("/update")
def update_patron_route( patron_id: int, first_name: Optional[str] = Query(None) , last_name :Optional[str] = Query(None) , email :Optional[str] = Query(None) ,
        phone_number : Optional[str] = Query(None)  ,service: PatronService = Depends(get_patron_service)):

    all_fields = { "first_name":first_name , "last_name":last_name , "email":email ,"phone_number":phone_number }
    updates = {field_name: value for field_name, value in all_fields.items() if value is not None}

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    return service.update_patron(patron_id=patron_id, updates=updates)