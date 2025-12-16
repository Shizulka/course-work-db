from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from contextlib import asynccontextmanager
from src.scheduler import start_scheduler
from src.routers import books, patron, checkout, waitlist, copy_book, author, genre, wishlist, relations, notification, analytics
from src.database import get_db, db_ping

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db_ping(db)
        return {"status": "ok", "message": "Підключення до Railway успішне!"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
    
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
