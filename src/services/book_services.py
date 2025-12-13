from fastapi import HTTPException
from src.repositories.book_repository import BookRepository
from src.models import Book

class BookService:
    def __init__(self , repo : BookRepository):
        self.repo = repo

    def get_book_list(self):
        book = self.repo.get_all

        if not book:
            return []
        return book
    
    def create_book(self, title: str, pages: int, publisher: str, language: str, year_published: str) :
    

        if pages <= 0:
             raise HTTPException(status_code=400, detail="There must be more than 0 pages")
        

        new_book = Book(
            title=title, 
            pages=pages, 
            publisher=publisher, 
            language=language,
            year_published=year_published
        )
    
        return self.repo.create(new_book)