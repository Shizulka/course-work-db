from sqlalchemy import text


def test_db_connection_select_1(engine):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar_one()
        assert result == 1


def test_session_can_execute_sql(db_session):
    result = db_session.execute(text("SELECT 2")).scalar_one()
    assert result == 2
