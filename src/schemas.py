from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    notification_id: int
    patron_id: int
    contents: str

class CheckoutResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    checkout_id: int  
    book_copy_id: int
    patron_id: int
    start_time: datetime
    end_time: datetime
    status: str

class BookCreate(BaseModel):
    title: str
    authors: List[str]
    pages: int
    publisher: str
    language: str
    year_published: int
    genres: List[str]
    price: int

class BookCreateWithCopies(BaseModel):
    title: str
    authors: List[str]
    year_published: int
    pages: int
    publisher: str
    language: str
    genres: List[str]
    price: int
    quantity: int = 1

class BookCopyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    book_copy_id: int
    copy_number: int

class AuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    author_id: int
    name: str

class GenreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    genre_id: int
    name: str

class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    book_id: int
    title: str
    author: List[AuthorResponse]
    year_published: int
    pages: int
    publisher: str
    language: str
    genre: List[GenreResponse]
    price: int
    copy_number: List[BookCopyResponse] = [] 
    

class BookInfoSimple(BaseModel):
    title: str 

class BookCopyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    book_copy_id: int
    copy_number: int
    available: int
    
    book: BookInfoSimple 
