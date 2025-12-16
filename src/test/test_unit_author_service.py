from src.services.author_services import AuthorService
from src.models import Author

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

class FakeAuthorRepo:
    def get_all(self):
        return [Author(author_id=1, name="Test Author")]

def test_create_author_unit():
    db = FakeDB()
    service = AuthorService(db=db, repo=None)

    author = service.create_author("80085")

    assert isinstance(author, Author)
    assert author.name == "80085"
    assert len(db.added) == 1
    assert db.committed is True
    assert author in db.refreshed


def test_get_author_list_unit():
    db = FakeDB()
    repo = FakeAuthorRepo()
    service = AuthorService(db=db, repo=repo)

    authors = service.get_author_list()

    assert isinstance(authors, list)
    assert len(authors) == 1
    assert authors[0].name == "Test Author"
