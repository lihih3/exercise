"""P0 tests: access rules where a wrong answer is a security hole or a lockout."""
import pytest

pytestmark = [pytest.mark.smoke, pytest.mark.regression]

TAG = "employee-A"


def test_new_tag_opens_main_door(system):
    """H1: the main door is the only entry point; denying it locks everyone out."""
    assert system.swipe(TAG, 1) is True, "New tag was refused at the main door"


def test_next_door_opens_after_previous_door_opened(open_path, system, clock):
    """H2: the core rule - opening the previous door unlocks the next one."""
    open_path(TAG, [1])
    clock.advance(2.0)
    assert system.swipe(TAG, 2) is True, "Door 2 refused although door 1 was opened"


def test_second_open_within_2_seconds_is_denied(open_path, system, clock):
    """B1: the 2-second limit is a security rule; just under 2s must be refused."""
    open_path(TAG, [1])
    clock.advance(1.999)
    assert system.swipe(TAG, 2) is False, "Door opened only 1.999s after the previous open"


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
    """N1-N3: skipping a door or using another branch must not bypass security."""
    open_path(TAG, already_opened)
    clock.advance(2.0)
    assert system.swipe(TAG, target) is False, (
        f"Door {target} opened although its previous door was never opened "
        f"(opened so far: {already_opened})"
    )


def test_other_employees_history_does_not_open_door(open_path, system, clock):
    """N4: access is personal; one employee's opens must not unlock doors for another."""
    open_path("employee-A", [1, 2])
    open_path("employee-B", [1])
    clock.advance(2.0)
    assert system.swipe("employee-B", 3) is False, (
        "Employee B opened door 3 using employee A's history"
    )


@pytest.mark.parametrize("bad_tag", ["", None], ids=["empty-string", "none"])
def test_empty_tag_is_denied_at_main_door(system, bad_tag):
    """N5: a blank or unreadable tag must never open the building's entry door."""
    assert system.swipe(bad_tag, 1) is False, f"Main door opened for empty tag {bad_tag!r}"
