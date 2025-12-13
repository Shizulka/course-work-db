from fastapi import HTTPException
from repositories.waitlist_repository import WaitlistRepository
from src.models import Waitlist

class WaitlistService:
    def __init__(self , repo : WaitlistRepository):
        self.repo = repo

    def get_waitlist_list(self):
        waitlist= self.repo.get_all

        if not waitlist:
            return []
        return waitlist
    
    def get_patron_position(self , book_id : int , patron_id : int )-> int:
        item = self.repo.get_by_patron_and_book(patron_id, book_id)

        if not item:
            return 0
        
        my_time = item.created_at
        count = self.repo.count_ahead(book_id, my_time)
        return count + 1
    
    def create_waitlist(self, book_id: int, patron_id: int ) :
    
        new_waitlist = Waitlist(
            book_id=book_id , 
            patron_id=patron_id)
    
        return self.repo.create(new_waitlist)
    
