from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics (SQL)"])

def get_analytics_service(db: Session = Depends(get_db)):
    return AnalyticsService(db)

@router.get("/top-patrons")
def read_top_patrons(service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_top_patrons()