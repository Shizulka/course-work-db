from sqlalchemy.orm import Session

class UltRepository:
    def __init__(self, db: Session, model):
        self.db = db
        self.model = model  

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def get_by_id(self, id: int):
        return self.db.get(self.model, id)

    def create(self, obj_data):
        self.db.add(obj_data)
        return obj_data

    def delete(self, obj):
        self.db.delete(obj)