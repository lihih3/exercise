import pytest

from rfid_access import AccessSystem, Door


class FakeClock:
    """Test clock: time moves only when the test calls advance()."""

    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def doors():
    """Layout from the task diagram: 1 -> 2 -> 3, 1 -> 6 -> 10, 1 -> 7 -> 11."""
    d = {i: Door(i) for i in (1, 2, 3, 6, 7, 10, 11)}
    d[1].add_next(d[2])
    d[2].add_next(d[3])
    d[1].add_next(d[6])
    d[6].add_next(d[10])
    d[1].add_next(d[7])
    d[7].add_next(d[11])
    return d


@pytest.fixture
def system(doors, clock):
    return AccessSystem(doors.values(), clock=clock)
