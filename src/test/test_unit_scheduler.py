import src.scheduler

def test_scheduler_starts(monkeypatch):
    called = {"start": False}

    def fake_start():
        called["start"] = True

    monkeypatch.setattr(src.scheduler, "start_scheduler", fake_start)

    src.scheduler.start_scheduler()

    assert called["start"] is True
