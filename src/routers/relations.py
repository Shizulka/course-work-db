from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.repositories.relations_repository import RelationsRepository
from src.services.relations_services import RelationsService

router = APIRouter(prefix="/relations", tags=["Relations"])

def get_relations_service(db: Session = Depends(get_db)):
    repo = RelationsRepository(db)
    return RelationsService(repo)

@router.post("/author-book")
def link_author_book(book_id: int, author_id: int, service: RelationsService = Depends(get_relations_service)):
    return service.add_author(book_id, author_id)

@router.post("/genre-book")
def link_genre_book(book_id: int, genre_id: int, service: RelationsService = Depends(get_relations_service)):
    return service.add_genre(book_id, genre_id)