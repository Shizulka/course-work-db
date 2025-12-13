from fastapi import HTTPException
from src.repositories.author_repository import AuthorRepository
from src.models import Author

class AuthorService:
    def __init__(self , repo :AuthorRepository):
        self.repo = repo

    def get_author_list(self):
        author = self.repo.get_all

        if not author:
            return []
        return author
    
    def create_author(self, name :str ) :
    
        new_author =Author(name=name)
    
        return self.repo.create(new_author)