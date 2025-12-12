from fastapi import HTTPException
from src.repositories.checkout_repositories import CheckoutRepositories
from src.models import Checkout
from datetime import datetime , timedelta

class CheckoutService:
    def __init__(self, repo: CheckoutRepositories):
        self.repo = repo

    def _update(self, checkout: Checkout):

        if not checkout.end_time:
            return

        now = datetime.now()

        if now > checkout.end_time:
            if checkout.status != "Overdue":
                checkout.status = "Overdue"
        
        elif checkout.end_time - now < timedelta(days=3):
            if checkout.status != "Soon":
                checkout.status = "Soon"
        
        else:
             if checkout.status != "OK":
                checkout.status = "OK"

    def get_checkout_list(self):
        # 1. Беремо дані
        checkouts = self.repo.get_all()
        print(f"--- ПОЧАТОК ПЕРЕВІРКИ: Знайдено {len(checkouts)} записів ---")

        if not checkouts:
            return []
        
        # 2. Оновлюємо кожен запис
        for item in checkouts:
            old_status = item.status
            self._update(item) # Викликаємо логіку перевірки дати
            
            # Пишемо в термінал, якщо статус змінився
            if old_status != item.status:
                print(f"🔄 ID {item.checkout_id}: Зміна статусу '{old_status}' -> '{item.status}'")
            else:
                print(f"⏹️ ID {item.checkout_id}: Статус без змін ({item.status})")
        
        # 3. ПРИМУСОВЕ ЗБЕРЕЖЕННЯ
        try:
            self.repo.db.commit()
            print("✅ Зміни успішно збережено в базу (COMMIT виконано)")
        except Exception as e:
            print(f"❌ ПОМИЛКА ЗБЕРЕЖЕННЯ: {e}")

        return checkouts
    
    
    def create_checkout(self, book_copy_id: int, patron_id: int, end_time: datetime):
        
        if not end_time:
            raise HTTPException(status_code=400, detail="End time is required")
        
        if end_time < datetime.now():
            raise HTTPException(status_code=400, detail="End time cannot be in the past")
        
        new_checkout = Checkout( book_copy_id=book_copy_id, patron_id=patron_id,end_time=end_time )
    
        return self.repo.create(new_checkout)