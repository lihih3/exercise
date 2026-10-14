"""P1/P2 tests: time boundary, re-opening doors, several employees."""
import pytest

pytestmark = pytest.mark.regression

TAG = "employee-A"


def open_path(system, clock, tag, path):
    """Open each door in order, 2s apart, so the time limit never blocks."""
    for door_id in path:
        clock.advance(2.0)
        assert system.swipe(tag, door_id), f"setup failed at door {door_id}"


@pytest.mark.parametrize(
    "wait", [2.0, 2.001], ids=["B2-exactly-2s-allowed", "B3-just-over-2s"]
)
def test_next_door_opens_at_or_after_2_seconds(system, clock, wait):
    open_path(system, clock, TAG, [1])
    clock.advance(wait)
    assert system.swipe(TAG, 2) is True


@pytest.mark.parametrize(
    "already_opened, target",
    [([1, 2], 2), ([1, 2, 3], 2)],
    ids=["H4-reopen-current-door", "E2-go-back-to-earlier-door"],
)
def test_door_already_opened_by_tag_opens_again(system, clock, already_opened, target):
    open_path(system, clock, TAG, already_opened)
    clock.advance(2.0)
    assert system.swipe(TAG, target) is True


def test_two_employees_same_moment_both_open(system):
    assert system.swipe("employee-A", 1) is True
    assert system.swipe("employee-B", 1) is True
