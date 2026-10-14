"""P0 tests: access rules where a wrong answer is a security hole or a lockout."""
import pytest

pytestmark = [pytest.mark.smoke, pytest.mark.regression]

TAG = "employee-A"


def test_new_tag_opens_main_door(system):
    assert system.swipe(TAG, 1) is True


def test_next_door_opens_after_previous_door_opened(open_path, system, clock):
    open_path(TAG, [1])
    clock.advance(2.0)
    assert system.swipe(TAG, 2) is True


def test_second_open_within_2_seconds_is_denied(open_path, system, clock):
    open_path(TAG, [1])
    clock.advance(1.999)
    assert system.swipe(TAG, 2) is False


@pytest.mark.parametrize(
    "already_opened, target",
    [
        ([], 2),
        ([1], 3),
        ([1, 2], 10),
    ],
    ids=[
        "N1-new-tag-skips-main-door",
        "N2-skips-door-2-to-reach-3",
        "N3-wrong-branch-door-10-without-6",
    ],
)
def test_door_denied_when_previous_not_opened(open_path, system, clock, already_opened, target):
    open_path(TAG, already_opened)
    clock.advance(2.0)
    assert system.swipe(TAG, target) is False


def test_other_employees_history_does_not_open_door(open_path, system, clock):
    open_path("employee-A", [1, 2])
    open_path("employee-B", [1])
    clock.advance(2.0)
    assert system.swipe("employee-B", 3) is False


@pytest.mark.parametrize("bad_tag", ["", None], ids=["empty-string", "none"])
def test_empty_tag_is_denied_at_main_door(system, bad_tag):
    assert system.swipe(bad_tag, 1) is False
