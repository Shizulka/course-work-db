from fastapi import HTTPException
from src.repositories.wishlist_repository import WishlistRepository
from src.models import Wishlist

class WishlistService:
    def __init__(self , repo : WishlistRepository):
        self.repo = repo

    def get_wishlist_list(self):
        wishlist = self.repo.get_all

        if not wishlist:
            return []
        return wishlist
    
    def create_wishlist(self ,patron_id: int ,title: str,  publisher: str,  language: str, year_published: int) :
    
        new_wishlist = Wishlist(
            patron_id=patron_id,
            title=title, 
            publisher=publisher, 
            language=language,
            year_published=year_published
        )
    
        return self.repo.create(new_wishlist)