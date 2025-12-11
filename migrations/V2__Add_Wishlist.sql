CREATE TABLE wishlist (
    wishlist_id SERIAL PRIMARY KEY,
    patron_id INT NOT NULL REFERENCES patron(patron_id),
    book_id INT NOT NULL REFERENCES book(book_id)
);

