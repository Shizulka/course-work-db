from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.repositories.author_repository import AuthorRepository
from src.services.author_services import AuthorService

router = APIRouter(prefix="/author", tags=["Author"])

def get_author_service(db: Session = Depends(get_db)) -> AuthorService:
    repo = AuthorRepository(db) 
    service = AuthorService(repo) 
    return service

@router.post("/")
def add_author( name : str ,service:  AuthorService = Depends(get_author_service)):
    return service.create_author( name=name ) 