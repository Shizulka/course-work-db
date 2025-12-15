from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.repositories.wishlist_repository import WishlistRepository
from src.services.wishlist_services import WishlistService

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


def get_wishlist_service(db: Session = Depends(get_db)) -> WishlistService:
    repo = WishlistRepository(db) 
    return WishlistService(repo) 

@router.post("/")
def add_wishlist(patron_id: int, title: str, author: str, publisher: str, language: str, year_published: int, service:WishlistService = Depends(get_wishlist_service)):
    return service.create_wishlist(patron_id=patron_id, title=title, author=author, publisher=publisher, language=language, year_published=year_published) 

@router.get("/")
def get_my_wishlist(
    patron_id: int,
    service: WishlistService = Depends(get_wishlist_service)
):
    return service.get_wishlist_by_patron(patron_id)