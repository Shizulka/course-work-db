from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.routers import books
from src.database import get_db

app = FastAPI()

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "Підключення до Railway успішне!"}
    except Exception as e:
        return {"status": "error", "details": str(e)}
    
app.include_router(books.router)

@app.get("/")
def root():
    return {"message": "Бібліотека працює!"}
