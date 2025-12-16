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
    
    def get_top_genre (self):
        sql = text("""
         WITH top_genre AS (
             SELECT 
                genre.name,
                COUNT(checkout.checkout_id) AS checkout_count
            FROM checkout 
                JOIN book_copy ON checkout.book_copy_id = book_copy.book_copy_id
                JOIN book ON book_copy.book_id = book.book_id
                JOIN book_genres ON book_genres.book_id = book.book_id
                JOIN genre ON genre.genre_id = book_genres.genre_id
                GROUP BY genre.name
                )
            SELECT *,
                ROW_NUMBER() OVER (
                    ORDER BY checkout_count DESC, name
                ) AS place
                FROM top_genre
                ORDER BY place
                LIMIT 5;
                   """)
        
        result = self.db.execute(sql).fetchall()

        return [{ "name": row[0], "checkout_count": row[1],   "rank": row[2] }
            for row in result 
        ]
