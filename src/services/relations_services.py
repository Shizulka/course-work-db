from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from src.repositories.relations_repository import RelationsRepository

class RelationsService:
    MAX_AUTHORS = 5
    MAX_GENRES = 7

    def __init__(self, repo: RelationsRepository):
        self.repo = repo

    def add_author(self, book_id: int, author_id: int):
        current_count = self.repo.count_authors_by_book(book_id)
        
        if current_count >= self.MAX_AUTHORS:
            raise HTTPException(
                status_code=400, 
                detail=f"Limit reached: A book cannot have more than {self.MAX_AUTHORS} authors."
            )

        try:
            self.repo.add_author_to_book(book_id, author_id)
            return {"message": "Author successfully linked to Book"}
        except IntegrityError:
            raise HTTPException(status_code=400, detail="This author is already linked to this book")

    def add_genre(self, book_id: int, genre_id: int):
        current_count = self.repo.count_genres_by_book(book_id)
        if current_count >= self.MAX_GENRES:
             raise HTTPException(
                status_code=400, 
                detail=f"Limit reached: A book cannot have more than {self.MAX_GENRES} genres."
            )

        try:
             self.repo.add_genre_to_book(book_id, genre_id)
             return {"message": "Genre successfully linked to Book"}
        except IntegrityError:
             raise HTTPException(status_code=400, detail="This genre is already linked to this book")