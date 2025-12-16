from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.scheduler import start_scheduler
from src.routers import books
from src.routers import patron
from src.routers import checkout
from src.routers import waitlist
from src.routers import copy_book
from src.routers import author
from src.routers import genre
from src.routers import wishlist
from src.routers import relations
from src.routers import notification
from src.routers import analytics
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
app.include_router(patron.router)
app.include_router(checkout.router)
app.include_router(waitlist.router)
app.include_router(copy_book.router)
app.include_router(author.router)
app.include_router(genre.router)
app.include_router(wishlist.router)
app.include_router(relations.router)
app.include_router(notification.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    return {"message": "Бібліотека працює!"}

@app.on_event("startup")
def startup_event():
    start_scheduler()