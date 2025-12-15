from fastapi import HTTPException
from src.repositories.author_repository import AuthorRepository
from src.models import Author
from sqlalchemy.orm import Session

class AuthorService:
    def __init__(self , db: Session, repo :AuthorRepository):
        self.db = db
        self.repo = repo

    def get_author_list(self):
        author = self.repo.get_all

        if not author:
            return []
        return author
    
    def create_author(self, name: str):
        new_author = Author(name=name)
       
        self.db.add(new_author)     
        self.db.commit()
        self.db.refresh(new_author)  
        return new_author
       