from sqlalchemy.orm import Session
from src.models import Patron

class PatronRepositories:
    def __init__(self,db : Session):
        self.db = db

    def get_all (self,skip: int = 0, limit: int = 100):
        return self.db.query(Patron).offset(skip).limit(limit).all()
    
    def create(self, patron_date):
        self.db.add(patron_date)
        self.db.commit()
        self.db.refresh(patron_date) 
        return patron_date
    
    def delete(self, patron_id: int):
        patron = self.db.query(Patron).filter(Patron.patron_id== patron_id).first()
        if patron:
            self.db.delete(patron)
            self.db.commit()