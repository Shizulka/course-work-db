from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from src.repositories.wishlist_repository import WishlistRepository
from src.models import Checkout, Wishlist, Notification, Patron
from src.templates import NotificationTemplates
from src.send_email_notification import send_email_notification

class WishlistService:
    def __init__(self , repo : WishlistRepository):
        self.repo = repo
        self.db = repo.db

    def get_wishlist_list(self):
        wishlist = self.repo.get_all()
        return wishlist or []

    def get_wishlist_by_patron(self, patron_id: int):
        patron = (self.repo.db.query(self.repo.model).filter(self.repo.model.patron_id == patron_id).all() )

        if not patron:
            raise HTTPException(status_code=404,detail=f"Not found")
       
        return patron
    
    def create_wishlist(self, patron_id: int, title: str, author: str, publisher: str, language: str, year_published: int) :
        if not patron:
            raise HTTPException(status_code=404, detail="Patron not found")
        
        if patron.status == "INACTIVE":
            raise HTTPException(status_code=404, detail="Patron is  inactive")
        
        
        active_checkouts = (
            self.db.query(Checkout)
            .filter(Checkout.patron_id == patron_id)
            .all()
        )
        
        for checkout in active_checkouts:
            self._update_status(checkout)
            if checkout.status == "Overdue":
                raise HTTPException(
                    status_code=403,
                    detail="You cannot borrow new books until overdue items are returned."
                )


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

                message_body = NotificationTemplates.WISHLIST_CREATED.format(
                    title=title
                )

                notification = Notification(
                    patron_id=patron_id,
                    contents=message_body
                )
                self.db.add(notification)

                patron = (
                    self.db.query(Patron)
                    .filter(Patron.patron_id == patron_id)
                    .first()
                )

                if patron and patron.email:
                    send_email_notification(
                        to_email=patron.email,
                        subject="Library: Wishlist request created",
                        message=message_body
                    )

                return {
                    "message": "Wishlist request created successfully",
                    "wishlist": new_wishlist
                }

        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail="Wishlist request already exists"
            )