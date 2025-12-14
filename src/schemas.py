
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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