from src.services.genre_services import GenreService
from src.models import Genre

class FakeDB:
    def __init__(self):
        self.added = []
        self.committed = False
        self.refreshed = []

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        self.refreshed.append(obj)

class FakeGenreRepo:
    def get_all(self):
        return [Genre(genre_id=1, name="Test Genre")]

def test_create_genre_unit():
    db = FakeDB()
    service = GenreService(db=db, repo=None)

    genre = service.create_genre("Unit Genre")

    assert isinstance(genre, Genre)
    assert genre.name == "Unit Genre"
    assert len(db.added) == 1
    assert db.committed is True
    assert genre in db.refreshed

def test_get_genre_list_unit():
    db = FakeDB()
    repo = FakeGenreRepo()
    service = GenreService(db=db, repo=repo)

    genres = service.get_genre_list()

    assert isinstance(genres, list)
    assert len(genres) == 1
    assert genres[0].name == "Test Genre"
