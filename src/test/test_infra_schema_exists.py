from sqlalchemy import inspect

EXPECTED_TABLES = {
    "author",
    "book",
    "genre",
    "patron",
    "book_copy",
    "notification",
    "waitlist",
    "wishlist",
    "checkout",
    "author_book",
    "book_genres",
}


def test_expected_tables_exist(engine):
    insp = inspect(engine)
    tables = set(insp.get_table_names())

    missing = EXPECTED_TABLES - tables
    assert not missing, f"Missing tables in DB: {sorted(missing)}"
