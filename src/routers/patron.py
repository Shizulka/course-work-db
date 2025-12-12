from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.repositories.patron_repositories import PatronRepositories
from src.services.patron_services import PatronService

router = APIRouter(prefix="/patrons", tags=["Patrons"])


def get_patron_service(db: Session = Depends(get_db)) -> PatronService:
    repo = PatronRepositories(db) 
    service = PatronService(repo) 
    return service

@router.post("/")
def add_patron(first_name: str, last_name: str, email: str, phone_number: str , service: PatronService = Depends(get_patron_service)):
    return service.create_patron(  first_name=first_name,  last_name=last_name,  email=email,  phone_number=phone_number) 

