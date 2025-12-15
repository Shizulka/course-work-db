from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from src.repositories.wishlist_repository import WishlistRepository
from src.models import Wishlist
from src.models import Notification

class WishlistService:
    def __init__(self , repo : WishlistRepository):
        self.repo = repo
        self.db = repo.db

    def get_wishlist_list(self):
        wishlist = self.repo.get_all()
        return wishlist or []

    def get_wishlist_by_patron(self, patron_id: int):
        wishlist = (
            self.repo.db
            .query(self.repo.model)
            .filter(self.repo.model.patron_id == patron_id)
            .all()
        )
        return wishlist or []
    
    def create_wishlist(self, patron_id: int, title: str, author: str, publisher: str, language: str, year_published: int) :
    
        try:
            with self.db.begin():

                new_wishlist = Wishlist(
                    patron_id=patron_id,
                    title=title,
                    author=author,
                    publisher=publisher,
                    language=language,
                    year_published=year_published
                )
                self.db.add(new_wishlist)

                notification = Notification(
                    patron_id=patron_id,
                    contents=(
                        f"Your request to add the book '{title}' "
                        f"has been successfully submitted."
                    )
                )
                self.db.add(notification)

                return {
                    "message": "Wishlist request created successfully",
                    "wishlist": new_wishlist
                }

        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail="Wishlist request already exists"
            )