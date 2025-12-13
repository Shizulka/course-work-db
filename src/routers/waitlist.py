from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from repositories.waitlist_repository import WaitlistRepository
from src.services.waitlist_services import WaitlistService

router = APIRouter(prefix="/waitlist", tags=["Waitlist"])

def get_waitlist_service(db: Session = Depends(get_db)) -> WaitlistService:
    repo = WaitlistRepository(db) 
    service = WaitlistService(repo) 
    return service

@router.get("/position")
def get_my_position(
    book_id: int, 
    patron_id: int, 
    service: WaitlistService = Depends(get_waitlist_service)
):
    pos = service.get_user_position(book_id, patron_id)
    if pos == 0:
        return {"message": "Ви не у черзі"}
    return {"message": f"Ваша позиція: {pos}"}


@router.post("/")
def add_waitlist( book_id: int, patron_id: int,  service: WaitlistService = Depends(get_waitlist_service)):
    return service.create_waitlist(book_id=book_id , patron_id=patron_id) 