import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def test_db_url() -> str:
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        raise RuntimeError(
            "TEST_DATABASE_URL is not set. "
            "Set it to a SEPARATE test database (not Railway prod)."
        )
    return url


@pytest.fixture(scope="session")
def engine(test_db_url):
    eng = create_engine(test_db_url, pool_pre_ping=True)
    # швидка перевірка, що зʼєднання реально є
    with eng.connect() as conn:
        conn.execute(text("SELECT 1"))
    return eng


@pytest.fixture()
def db_session(engine):
    """
    Один тест = одна транзакція, в кінці rollback.
    Це дозволяє 'очищати БД' між тестами без TRUNCATE.
    """
    connection = engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
