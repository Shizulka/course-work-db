from fastapi import HTTPException
from src.repositories.genre_repository import GenreRepository
from src.models import Genre

class GenreService:
    def __init__(self , repo :GenreRepository):
        self.repo = repo

    def get_genre_list(self):
        genre = self.repo.get_all

        if not genre:
            return []
        return genre
    
    def create_genre(self, name :str ) :
    
        new_genre=Genre(name=name)
    
        return self.repo.create(new_genre)