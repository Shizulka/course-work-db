from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.schemas import BookCreateWithCopies
from src.repositories.book_repository import BookRepository
from src.models import Book, BookCopy

class BookService:
    def __init__(self, db: Session, repo: BookRepository):
        self.db = db
        self.repo = repo

    def get_book_list(self):
        book = self.repo.get_all

        if not book:
            return []
        return book
    
    def create_book_with_copies(self, data: BookCreateWithCopies):
        try:
        
            new_book = Book(
                title=data.title,
                year_published=data.year_published,
                pages=data.pages,
                publisher=data.publisher,
                language=data.language
            )
            self.db.add(new_book)
            
            self.db.flush() 
            
            copy = BookCopy(
                book_id=new_book.book_id,
                available=data.quantity,
                copy_number=data.quantity
            )
            self.db.add(copy)

            self.db.commit()
            self.db.refresh(new_book)
            return new_book
            
        except IntegrityError:
            self.db.rollback() 
            raise HTTPException(status_code=400, detail="This book already exists")


    def create_book(self, title: str, pages: int, publisher: str, language: str, year_published: str) :
    

        if pages <= 0:
             raise HTTPException(status_code=400, detail="There must be more than 0 pages")
        

        new_book = Book( 
            title=title ,  
            publisher=publisher ,
            language=language , 
            year_published=year_published
        )
    
        try:
             self.repo.create(new_book)
             return {"message": "The book has been successfully added"}
        except IntegrityError:
             raise HTTPException(status_code=400, detail="This book already exists")