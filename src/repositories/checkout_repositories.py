from sqlalchemy.orm import Session
from src.models import Checkout

class CheckoutRepositories:
    def __init__(self,db : Session):
        self.db = db

    def get_all (self,skip: int = 0, limit: int = 100):
        return self.db.query(Checkout).offset(skip).limit(limit).all()
    

    
    def create(self, checkout_data):
        self.db.add(checkout_data)
        self.db.commit()
        self.db.refresh(checkout_data) 
        return checkout_data
    
    def delete(self, checkout_id: int):
        checkout = self.db.query(Checkout).filter(Checkout.checkout_id == checkout_id).first()
        if checkout:
            self.db.delete(checkout)
            self.db.commit()