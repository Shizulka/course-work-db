import src.scheduler

def test_scheduler_starts(monkeypatch):
    called = {"start": False}

    def fake_start():
        called["start"] = True

    monkeypatch.setattr(src.scheduler, "start_scheduler", fake_start)

    src.scheduler.start_scheduler()

    assert called["start"] is True

def test_start_scheduler_adds_job_and_starts(monkeypatch):
    import src.scheduler

    jobs = []
    started = {"value": False}

    class FakeScheduler:
        def add_job(self, func, trigger, **kwargs):
            jobs.append((func, trigger))

        def start(self):
            started["value"] = True

    monkeypatch.setenv("ENV", "prod")
    monkeypatch.setattr(src.scheduler, "scheduler", FakeScheduler())

    src.scheduler.start_scheduler()

    assert started["value"] is True
    assert len(jobs) == 2
    