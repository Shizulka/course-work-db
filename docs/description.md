
##  Перелік таблиць та обмежень схеми 

---

### AUTHOR – зберігає авторів 

| Поле | Тип | Опис |
| :--- | :--- | :--- |
| author_id | integer **PK** | Унікальний ID автора  |
| name | varchar(50) | Імʼя автора  |

---

###  BOOK – зберігає книги 

| Поле | Тип | Опис |
| :--- | :--- | :--- |
| book_id | integer **PK** | Унікальний ID книги  |
| title | varchar(255) | Назва  |
| author_id | integer **PK** | ID автора – **зовнішній ключ**, що посилається на `Author(author_id)` |
| genre_id | varchar(255) | ID жанру – **зовнішній ключ**, що посилається на `Genre(genre_id)`  |
| language | varchar(255) | Мова |
| year_published | integer | Рік видання |
| pages | integer | К-сть сторінок (**>0**) |
| publisher | varchar(255) | Назва видавництва | 
| price | integer | Ціна книги |

---

###  BOOK_COPY – зберігає окремі екземпляри книг 

| Поле | Тип | Опис |
| :--- | :--- | :--- |
| book_copy_id | integer (**PK**) | ID копії  |
| book_id | integer (**FK → book**) |ID книги – **зовнішній ключ**, що посилається на `Book(book_id)` |
| copy_number | varchar(255) | Кількість копій  |

---

###  GENRE – зберігає жанри книг 

| Поле | Тип | Опис |
| :--- | :--- | :--- |
| genre_id | integer (**PK**) | ID жанру  |
| name | varchar(100) **UNIQUE** | Назва жанру  |

---

### PATRON – зберігає користувачів 

| Поле | Тип | Опис |
| :--- | :--- | :--- |
| patron_id | integer (**PK**) | ID користувача |
| first_name | varchar(50) | Ім’я |
| last_name | varchar(50) | Прізвище |
| email | varchar(100) **UNIQUE** | Email |
| phone_number | varchar(50) | Телефон |

---

### CHECKOUT – реєстрація виданих книг

| Поле | Тип | Опис |
| :--- | :--- | :--- |
| checkout_id | integer (**PK**) | ID видачі |
| book_copy_id | integer (**FK → book_copy**) | ID копії – **зовнішній ключ**, що посилається на `Book_copy(book_copy_id)` |
| patron_id | integer (**FK → patron**) | ID користувача – **зовнішній ключ**, що посилається на `Patron(patron_id)` |
| start_time | timestamp (**DEFAULT now()**) | Дата початку видачі |
| end_time | timestamp | Дата повернення |
| sttus | enum | чи книга на руках |

---

### NOTIFICATION – зберігає сповіщення 

| Поле | Тип | Опис |
| :--- | :--- | :--- |
| notification_id | integer (**PK**) | ID сповіщення  |
| patron_id | integer (**FK → patron**) | ID користувача – **зовнішній ключ**, що посилається на `Patron(patron_id)` |
| contents | text | [cite_start]Текст повідомлення |

---

### WAITLIST – зберігає чергу очікування 
| Поле | Тип | Опис |
| :--- | :--- | :--- |
| waitlist_id | integer (**PK**) | ID запису |
| patron_id | integer (**FK → patron**) | ID користувача – **зовнішній ключ**, що посилається на `Patron(patron_id)` |
| book_id | integer (**FK → book**) | ID книги – **зовнішній ключ**, що посилається на `Book(book_id)` |

---


