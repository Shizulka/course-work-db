from fastapi import HTTPException
from src.repositories.copy_book_repository import BookCopyRepository
from src.models import BookCopy

class BookCopyService:
    def __init__(self , repo : BookCopyRepository):
        self.repo = repo

    def get_copy_book_list(self):
        copy_book = self.repo.get_all

        if not copy_book:
            return []
        return copy_book
    

    
    def create_book(self, book_id: int , copy_number: int , available :int  ):
    
        new_copy_book = BookCopy ( 
          book_id=book_id,
          copy_number= copy_number,
          available=available
        )
    
        return self.repo.create(new_copy_book)