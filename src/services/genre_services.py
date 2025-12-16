from fastapi import HTTPException
from src.repositories.genre_repository import GenreRepository
from src.models import Genre
from sqlalchemy.orm import Session

class GenreService:
    def __init__(self , db: Session, repo :GenreRepository):
        self.repo = repo
        self.db = db

    def get_genre_list(self):
        genre = self.repo.get_all()

        if not genre:
            return []
        return genre
    
    def create_genre(self, name :str ) :
    
        new_genre=Genre(name=name)
    
        self.db.add(new_genre)     
        self.db.commit()
        self.db.refresh(new_genre)  
        return new_genre