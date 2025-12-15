from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class NotificationResponse(BaseModel):
    notification_id: int
    patron_id: int
    contents: str

    class Config:
        from_attributes = True 

class CheckoutResponse(BaseModel):
    checkout_id: int  
    book_copy_id: int
    patron_id: int
    start_time: datetime
    end_time: datetime
    status: str

    class Config:
        from_attributes = True


class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    year_published: int

class BookCreate(BookBase):
    pass

class BookCreateWithCopies(BaseModel):
    title: str
    year_published: int
    pages: int
    publisher: str
    language: str
    quantity: int = 1

class BookCopyResponse(BaseModel):
    book_copy_id: int
    copy_number: int
    class Config:
        from_attributes = True

class BookResponse(BaseModel):
    book_id: int
    title: str
    year_published: int
    pages: int
    publisher: str
    language: str
    copy_number: List[BookCopyResponse] = [] 
    
    class Config:
        from_attributes = True

class BookInfoSimple(BaseModel):
    title: str 

class BookCopyResponse(BaseModel):
    book_copy_id: int
    copy_number: int
    available: int
    
    book: BookInfoSimple 

    class Config:
        from_attributes = True