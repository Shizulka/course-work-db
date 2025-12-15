from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.repositories.genre_repository import GenreRepository
from src.services.genre_services import GenreService

router = APIRouter(prefix="/genre", tags=["Genre"])

def get_genre_service(db: Session = Depends(get_db)) -> GenreService:
    repo = GenreRepository(db) 
    service = GenreService(db, repo) 
    return service

@router.post("/")
def add_genre( name : str ,service:  GenreService = Depends(get_genre_service)):
    return service.create_genre( name=name ) 