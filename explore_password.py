"""
Exploratory check for is_password_valid against TEST_PLAN.md.
Each case: (plan ID, input, expected). Expected is True/False, TypeError,
or "?" for open questions where the spec is silent (result is shown, not judged).
"""
from device_posture import is_password_valid

OPEN = "?"

cases = [
    # 1.1 Happy path
    ("PW-01", "Passw0rd!", True),
    # 1.2 Boundary: length 7 / 8 / 9
    ("PW-02", "Abcde1!", False),
    ("PW-03", "Abcdef1!", True),
    ("PW-04", "Abcdefg1!", True),
    # 1.3 Decision table: upper / digit / special (all 8 combinations)
    ("PW-05", "passw0rd!", False),   # no upper
    ("PW-06", "Password!", False),   # no digit
    ("PW-07", "Passw0rd", False),    # no special
    ("PW-08", "password!", False),   # special only
    ("PW-25", "Password", False),    # upper only
    ("PW-26", "passw0rd", False),    # digit only
    ("PW-27", "password", False),    # none
    # 1.4 Special characters not on the allowed list
    ("PW-09", "Passw0rd?", False),
    ("PW-10", "Passw0rd_", False),
    ("PW-11", "Passw0rd ", False),   # trailing space
    ("PW-28", "Passw0rd\t", False),  # tab
    ("PW-29", "Passw0rd\n", False),  # newline
    # Every allowed special character is accepted
    *[(f"PW-30{c}", f"Passw0rd{c}", True) for c in "!@#$%^&*"],
    # Position of the required characters
    ("PW-31", "!Passw0rd", True),    # special first
    ("PW-32", "P@ssw0rd", True),     # special in the middle
    ("PW-33", "1Password!", True),   # digit first
    # Not over-enforcing: lowercase is NOT required
    ("PW-34", "PASSW0RD!", True),
    # 1.5 Negative: wrong type -> TypeError
    ("PW-12", None, TypeError),
    ("PW-13", 12345678, TypeError),
    ("PW-14", object(), TypeError),
    ("PW-15", b"Passw0rd!", TypeError),
    ("PW-16", list("Passw0rd!"), TypeError),
    ("PW-17", set("Passw0rd!"), TypeError),
    ("PW-18", dict.fromkeys("Passw0rd!"), TypeError),
    # 1.6 Edge cases
    ("PW-19", "", False),
    ("PW-20", " " * 8, False),
    ("PW-21", "Pass w0rd!", True),
    ("PW-22", "A1!" + "a" * 1000, True),
    # Open questions (spec is silent)
    ("PW-23", "Äbcdefg1!", OPEN),    # non-ASCII uppercase
    ("PW-24", "Abcdefg٣!", OPEN),    # non-ASCII digit
    ("PW-35", "Pa$s1😀😀", OPEN),     # emoji: how is length counted?
]

counts = {"PASS": 0, "FAIL": 0, "OPEN": 0}
for case_id, pw, expected in cases:
    try:
        actual = is_password_valid(pw)
    except Exception as e:
        actual = type(e)
        actual_text = f"{type(e).__name__}: {e}"
    else:
        actual_text = repr(actual)

    if expected is OPEN:
        status = "OPEN"
    else:
        status = "PASS" if actual == expected else "FAIL"
    counts[status] += 1

    expected_text = expected.__name__ if isinstance(expected, type) else repr(expected)
    shown = repr(pw) if len(repr(pw)) <= 30 else repr(pw)[:27] + "..."
    print(f"{status:4}  {case_id:7} {shown:32} expected={expected_text:10} actual={actual_text}")

print(f"\n{counts['PASS']} passed, {counts['FAIL']} failed, {counts['OPEN']} open questions")
