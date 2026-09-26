"""
Tests for is_password_valid. Case IDs (PW-xx) refer to TEST_PLAN.md.
Tests that expose a bug are expected to FAIL until the bug is fixed (see BUGS.md).
"""
import pytest

from device_posture import is_password_valid


# Passwords that meet all four rules -> True
VALID_PASSWORDS = {
    "PW-01 happy path": "Passw0rd!",
    "PW-03 exactly 8 chars": "Abcdef1!",
    "PW-04 9 chars": "Abcdefg1!",
    "PW-21 space inside": "Pass w0rd!",
    "PW-22 very long": "A1!" + "a" * 1000,
    "PW-31 special first": "!Passw0rd",
    "PW-32 special in middle": "P@ssw0rd",
    "PW-33 digit first": "1Password!",
    "PW-34 no lowercase needed": "PASSW0RD!",
    # PW-30: every allowed special character is accepted
    **{f"PW-30 special {c}": f"Passw0rd{c}" for c in "!@#$%^&*"},
}

# Passwords that break at least one rule -> False
INVALID_PASSWORDS = {
    "PW-02 7 chars": "Abcde1!",
    # Decision table: upper / digit / special
    "PW-05 no upper": "passw0rd!",
    "PW-06 no digit": "Password!",
    "PW-07 no special": "Passw0rd",
    "PW-08 special only": "password!",
    "PW-25 upper only": "Password",
    "PW-26 digit only": "passw0rd",
    "PW-27 no rule met": "password",
    # Characters that are not allowed special characters
    "PW-09 question mark": "Passw0rd?",
    "PW-10 underscore": "Passw0rd_",
    "PW-11 trailing space": "Passw0rd ",
    "PW-28 tab": "Passw0rd\t",
    "PW-29 newline": "Passw0rd\n",
    # Edge cases
    "PW-19 empty string": "",
    "PW-20 8 spaces": " " * 8,
}

# Inputs that are not strings -> TypeError
NON_STRING_INPUTS = {
    "PW-12 None": None,
    "PW-13 int": 12345678,
    "PW-14 object": object(),
    "PW-15 bytes": b"Passw0rd!",
    "PW-16 list of chars": list("Passw0rd!"),
    "PW-17 set of chars": set("Passw0rd!"),
    "PW-18 dict of chars": dict.fromkeys("Passw0rd!"),
}


@pytest.mark.parametrize("password", VALID_PASSWORDS.values(), ids=VALID_PASSWORDS.keys())
def test_valid_password_is_accepted(password):
    assert is_password_valid(password) is True


@pytest.mark.parametrize("password", INVALID_PASSWORDS.values(), ids=INVALID_PASSWORDS.keys())
def test_invalid_password_is_rejected(password):
    assert is_password_valid(password) is False


@pytest.mark.parametrize("password", NON_STRING_INPUTS.values(), ids=NON_STRING_INPUTS.keys())
def test_non_string_raises_type_error(password):
    with pytest.raises(TypeError):
        is_password_valid(password)
