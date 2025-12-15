from fastapi import HTTPException
from src.repositories.copy_book_repository import BookCopyRepository
from src.models import BookCopy
from sqlalchemy.orm import Session

class BookCopyService:
    def __init__(self ,db: Session, repo : BookCopyRepository):
        self.repo = repo
        self.db = db

    def get_copy_book_list(self):
        copy_book = self.repo.get_all

        if not copy_book:
            return []
        return copy_book
    
    def update_available(self, book_id: int, copy_number: int):
        copy_book = self.db.query(BookCopy).filter(BookCopy.book_id == book_id).first()

        if not copy_book:
            raise HTTPException(status_code=404, detail="The book does not exist")
        
        borrowed_count = copy_book.copy_number - copy_book.available

        copy_book.available = copy_number - borrowed_count
        copy_book.copy_number = copy_number

        self.db.commit()
        self.db.refresh(copy_book)
        
        return copy_book
    
    def create_copy_book(self, book_id: int , copy_number: int , available :int  ):

        if copy_number < 0:
             raise HTTPException(status_code=400,detail="The number of books cannot be less than 0." )
        
        if  copy_number < available:
            raise HTTPException(status_code=400,detail="The number of available books cannot exceed the total number." )
        
        if available < 0:
             raise HTTPException(status_code=400,detail="The number of books cannot be less than 0." )
    
        new_copy_book = BookCopy ( 
          book_id=book_id,
          copy_number= copy_number,
          available=available
        )
    
        self.db.add(new_copy_book)     
        self.db.commit()
        self.db.refresh(new_copy_book)  
        return new_copy_book