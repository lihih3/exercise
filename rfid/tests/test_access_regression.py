"""P1/P2 tests: time boundary, re-opening doors, several employees."""
import pytest

pytestmark = pytest.mark.regression

TAG = "employee-A"


@pytest.mark.parametrize(
    "wait", [2.0, 2.001], ids=["B2-exactly-2s-allowed", "B3-just-over-2s"]
)
def test_next_door_opens_at_or_after_2_seconds(open_path, system, clock, wait):
    """B2-B3: a swipe at or after 2s is allowed; catches an off-by-one (< vs <=)."""
    open_path(TAG, [1])
    clock.advance(wait)
    assert system.swipe(TAG, 2) is True, f"Door 2 refused {wait}s after the previous open"


@pytest.mark.parametrize(
    "already_opened, target",
    [([1, 2], 2), ([1, 2, 3], 2)],
    ids=["H4-reopen-current-door", "E2-go-back-to-earlier-door"],
)
def test_door_already_opened_by_tag_opens_again(open_path, system, clock, already_opened, target):
    """H4/E2: a door this tag already opened must open again, or employees get locked in."""
    open_path(TAG, already_opened)
    clock.advance(2.0)
    assert system.swipe(TAG, target) is True, (
        f"Door {target} refused although this tag already opened it ({already_opened})"
    )


def test_two_employees_same_moment_both_open(system):
    """E1: the 2-second limit is per employee, so colleagues must not block each other."""
    assert system.swipe("employee-A", 1) is True, "Employee A refused at the main door"
    assert system.swipe("employee-B", 1) is True, (
        "Employee B refused because employee A swiped at the same moment"
    )


def test_denied_swipe_does_not_start_the_wait(open_path, system, clock):
    """E4: only a real open starts the 2s wait; a wrong swipe must not cause a lockout."""
    open_path(TAG, [1])
    clock.advance(2.0)
    assert system.swipe(TAG, 3) is False, "Setup: door 3 should be refused (door 2 not opened)"
    clock.advance(1.0)
    assert system.swipe(TAG, 2) is True, (
        "Door 2 refused 3s after the last real open - the denied swipe restarted the wait"
    )


def test_unknown_door_raises_clear_error(system):
    """N6: a misconfigured reader must get a clear error, not a crash or an open door."""
    with pytest.raises(ValueError, match="Unknown door: 99"):
        system.swipe(TAG, 99)
