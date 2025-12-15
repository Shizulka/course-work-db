### Запит №1: Перегляд топ-5 найактивніших користувачів

```sql
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
```

Цей запит відображає дані топ-5 найактивніших користувачів.

Активність визначається за найбільшою кількістю взятих книг (мінімум 2)