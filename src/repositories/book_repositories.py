from sqlalchemy.orm import Session
from src.models import Book

class BookRepositories:
    def __init__(self,db : Session):
        self.db = db

    def get_all (self,skip: int = 0, limit: int = 100):
        return self.db.query(Book).offset(skip).limit(limit).all()
    
    def create(self, book_data):
        self.db.add(book_data)
        self.db.commit()
        self.db.refresh(book_data) 
        return book_data
    
    def delete(self, book_id: int):
        book = self.db.query(Book).filter(Book.book_id == book_id).first()
        if book:
            self.db.delete(book)
            self.db.commit()