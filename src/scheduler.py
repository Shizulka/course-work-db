from apscheduler.schedulers.background import BackgroundScheduler
from src.database import SessionLocal
from src.repositories.checkout_repository import CheckoutRepository
from src.repositories.copy_book_repository import BookCopyRepository
from src.services.checkout_services import CheckoutService

def update_checkout_status_job():
    db = SessionLocal()
    try:
        checkout_repo = CheckoutRepository(db)
        book_copy_repo = BookCopyRepository(db)
        service = CheckoutService(checkout_repo, book_copy_repo)
        service.update_all_checkout_statuses()
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        update_checkout_status_job,
        "interval",
        minutes=1 #такий час виключно для швидкої демонстрації. для реального застосування краще використовувати шось типу 1-2 рази на день, за умови, що ми кінцевий термін будемо на один і той самий час ставити
    )
    scheduler.start()
