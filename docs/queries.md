## 4. Прості SELECT-запити

Пошук автора конкретної  книги 

```sql
SELECT 
	book.title,
	author.name
FROM author
	JOIN author_book ON author_book.author_id = author.author_id 
	JOIN book ON author_book.book_id = book.book_id
WHERE  book.title = 'Мотанка' 
LIMIT 5 OFFSET 0

```
Перевірка наявності примірників  конкретної книги

```sql
SELECT 
	book.title,
	book_copy.copy_number,
	book_copy.available
FROM book 
	join book_copy ON book_copy.book_id=book.book_id
WHERE  book.title = '1984'
```

## 5. Складні аналітичні запити


### Запит №1: Перегляд топ-5 найактивніших користувачів

Шлях -> src/services/analytics_service.py  ->  get_top_patrons


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

---
---

## Запит №2: Перегляд топ 5 жанрів 

Шлях -> src/services/analytics_service.py  -> get_top_genre

```sql
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

```
Цей запит показує топ-5 найпопулярніших жанрів.

Популярність визначається за найбільшою кількістю книжок певного жанру.
