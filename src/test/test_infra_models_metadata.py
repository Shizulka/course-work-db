from src.models import Base


def test_models_metadata_has_expected_tables():
    tables = set(Base.metadata.tables.keys())

    # Base.metadata.tables включає і таблиці звʼязків (author_book, book_genres)
    expected = {
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

    missing = expected - tables
    assert not missing, f"Missing tables in Base.metadata: {sorted(missing)}"
