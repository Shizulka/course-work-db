from sqlalchemy.orm import Session
from sqlalchemy import text

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_top_patrons(self):
        sql = text("""
        WITH patron_activity AS (
         SELECT
            p.patron_id,
            p.first_name,
            p.last_name,
            p.email,
            COUNT(c.checkout_id) AS checkout_count
        FROM checkout c
         JOIN patron p ON c.patron_id = p.patron_id
         JOIN book_copy bc ON c.book_copy_id = bc.book_copy_id
         GROUP BY p.patron_id, p.first_name, p.last_name, p.email
         HAVING COUNT(c.checkout_id) >= 2
        )
        SELECT
            *,
            RANK() OVER (ORDER BY checkout_count DESC) AS activity_rank
            FROM patron_activity
            ORDER BY checkout_count DESC
            LIMIT 5;
        """)
        
        result = self.db.execute(sql).fetchall()
        
        return [  {"patron_id": row[0], "full_name": f"{row[1]} {row[2]}", "email": row[3],"checkout_count": row[4],"rank": row[5] }
            for row in result
        ]