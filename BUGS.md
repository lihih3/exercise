# Bug Reports – `device_posture.py`

Found by exploratory testing against the spec (the docstring of each function).
All steps assume a Python console opened in the repository root.

**Severity scale**
- **Critical:** a false green (an insecure device is reported as safe) or a device left in a broken state. Direct security risk for the customer.
- **High:** wrong result in the dangerous direction for some inputs, or the feature fails on valid input.
- **Medium:** wrong but safe result (a false red), or wrong handling of invalid input that could plausibly occur.
- **Low:** wrong handling of input that is invalid and unlikely.

## Summary

| ID | Title | Severity |
|----|-------|----------|
| BUG-01 | Password policy accepts passwords that miss required rules | Critical |
| BUG-02 | Open-port check passes a device when only one port is allowed | Critical |
| BUG-03 | Scans older than 24 hours are never reported as stale | Critical |
| BUG-04 | Rollback is never called when remediation fails | Critical |
| BUG-05 | Outdated OS versions are reported as supported | High |
| BUG-06 | Remediation makes one attempt fewer than `max_attempts` | High |
| BUG-07 | Risk score 70 is classified as MEDIUM instead of HIGH | High |
| BUG-08 | Uppercase severity values crash the risk score | High |
| BUG-09 | Device with no open ports is reported as non-compliant | Medium |
| BUG-10 | Password check accepts non-string inputs instead of raising TypeError | Medium |
| BUG-11 | Risk level accepts scores outside 0–100 | Low |
| BUG-12 | `max_attempts < 1` does not raise ValueError | Low |

**Open question (not a bug until the spec is clarified):** `is_os_version_supported("13", "13.0")` returns `False`. Should `"13"` equal `"13.0"`?

---

## BUG-01 – Password policy accepts passwords that miss required rules

**Severity:** Critical
**Function:** `is_password_valid`
**Test plan cases:** PW-05 to PW-11, PW-28, PW-29

**Steps to reproduce**
```python
from device_posture import is_password_valid
is_password_valid("password!")   # no uppercase, no digit
is_password_valid("Passw0rd")    # no special character
```

**Expected:** `False` for both. The spec requires ALL four rules.
**Actual:** `True` for both.

There are two failure modes:
1. A special character alone is enough (`"password!"`, `"Password!"`, `"passw0rd!"`).
2. Uppercase + digit is enough, so the special-character rule is never enforced (`"Passw0rd"`, `"Passw0rd?"`, `"Passw0rd "`).

**Customer impact:** Weak passwords are accepted and the device is reported as compliant. The customer's dashboard is green while local accounts are easier to brute-force.

**Root cause:** `if has_upper and has_digit or has_special` is evaluated as `(has_upper and has_digit) or has_special`, because `and` binds tighter than `or`.

**Suggested fix:** `return has_upper and has_digit and has_special`

---

## BUG-02 – Open-port check passes a device when only one port is allowed

**Severity:** Critical
**Function:** `is_port_configuration_compliant`

**Steps to reproduce**
```python
from device_posture import is_port_configuration_compliant
is_port_configuration_compliant([22, 3389], [22, 443])
```

**Expected:** `False`. RDP (3389) is not allowed. This is the spec's own example.
**Actual:** `True`

**Customer impact:** A device with an unauthorized open port (RDP, a common ransomware entry point) is reported as compliant as long as at least one of its open ports is allowed.

**Root cause:** `any(...)` is used where the spec ("EVERY open port") requires `all(...)`.

**Suggested fix:** `return all(port in allowed_ports for port in open_ports)` (this also fixes BUG-09).

---

## BUG-03 – Scans older than 24 hours are never reported as stale

**Severity:** Critical
**Function:** `is_scan_stale`

**Steps to reproduce**
```python
from datetime import datetime, timedelta
from device_posture import is_scan_stale
now = datetime(2026, 9, 26, 12, 0, 0)
is_scan_stale(now - timedelta(hours=24, seconds=1), now)
is_scan_stale(now - timedelta(hours=49), now)
is_scan_stale(now - timedelta(days=7), now)
```

**Expected:** `True` for all three.
**Actual:** `False` for all three.

**Customer impact:** The posture shown to the customer can be days or weeks old and still look current. A device that stopped reporting (agent crashed or was removed by an attacker) keeps its last "compliant" status.

**Root cause:** `elapsed.seconds` is only the seconds part of the `timedelta` (0–86399) and ignores `.days`. 49 hours gives `days=2, seconds=3600`, so it compares 3600 > 86400.

**Suggested fix:** `return elapsed > STALE_AFTER`

---

## BUG-04 – Rollback is never called when remediation fails

**Severity:** Critical
**Function:** `RemediationEngine.remediate`

**Steps to reproduce**
```python
from unittest.mock import Mock
from device_posture import RemediationEngine, RemediationFailed
executor = Mock()
executor.apply.return_value = False
try:
    RemediationEngine(executor).remediate("dev1", "fix")
except RemediationFailed:
    pass
executor.rollback.call_count
```

**Expected:** `RemediationFailed` is raised and `rollback` is called exactly once with `("dev1", "fix")`.
**Actual:** `RemediationFailed` is raised, but `rollback.call_count == 0`.

**Customer impact:** A fix that fails partway can leave the device half-changed (for example, a service stopped but not reconfigured). Without rollback, the customer's device can end up broken or less secure than before remediation.

**Root cause:** The code raises `RemediationFailed` without calling `executor.rollback`.

**Suggested fix:** Call `self.executor.rollback(device_id, fix_name)` once, after the retry loop and before raising.

---

## BUG-05 – Outdated OS versions are reported as supported

**Severity:** High
**Function:** `is_os_version_supported`

**Steps to reproduce**
```python
from device_posture import is_os_version_supported
is_os_version_supported("9.0", "13.0")
is_os_version_supported("13.10", "13.9")
```

**Expected:** `False` for the first, `True` for the second.
**Actual:** `True` for the first, `False` for the second.

**Customer impact:** Old, unpatched OS versions (9.x when 13.0 is required) pass the check, so vulnerable devices are reported as compliant. In the other direction, valid newer versions such as 13.10 are flagged as unsupported.

**Root cause:** The versions are compared as strings, character by character (`"9" > "1"`), not as numbers.

**Suggested fix:** Compare tuples of integers, e.g. `tuple(map(int, version.split(".")))`, padding with zeros to equal length (which also answers the open question for `"13"` vs `"13.0"`).

---

## BUG-06 – Remediation makes one attempt fewer than `max_attempts`

**Severity:** High
**Function:** `RemediationEngine.remediate`

**Steps to reproduce**
```python
from unittest.mock import Mock
from device_posture import RemediationEngine
executor = Mock()
executor.apply.side_effect = [False, False, True]
RemediationEngine(executor, max_attempts=3).remediate("dev1", "fix")
```

**Expected:** Returns `3`, and `apply.call_count == 3`.
**Actual:** Raises `RemediationFailed`, and `apply.call_count == 2`.

**Customer impact:** Fixes that would succeed on the last allowed attempt are reported as failed, so devices stay non-compliant and need manual work. With `max_attempts=1`, no attempt is made at all.

**Root cause:** `range(1, self.max_attempts)` stops at `max_attempts - 1`.

**Suggested fix:** `range(1, self.max_attempts + 1)`

---

## BUG-07 – Risk score 70 is classified as MEDIUM instead of HIGH

**Severity:** High
**Function:** `get_risk_level`

**Steps to reproduce**
```python
from device_posture import get_risk_level
get_risk_level(70)
```

**Expected:** `"HIGH"` (the spec says 70–100 is HIGH).
**Actual:** `"MEDIUM"`

**Customer impact:** A device on the HIGH boundary is under-reported. Any alerting or prioritization triggered by HIGH risk will miss it.

**Root cause:** `score > 70` should be `score >= 70`.

**Suggested fix:** `if score >= 70:`

---

## BUG-08 – Uppercase severity values crash the risk score

**Severity:** High
**Function:** `calculate_risk_score`

**Steps to reproduce**
```python
from device_posture import calculate_risk_score
calculate_risk_score([{"id": "a", "severity": "HIGH"}])
```

**Expected:** `30`. The spec says severity is case-insensitive.
**Actual:** `ValueError: Unknown severity: HIGH`

**Customer impact:** If a scanner reports severities in uppercase or mixed case, the whole risk calculation fails for that device, and no risk score is shown to the customer.

**Root cause:** The severity is looked up without normalizing its case.

**Suggested fix:** `severity = finding["severity"].lower()`

---

## BUG-09 – Device with no open ports is reported as non-compliant

**Severity:** Medium
**Function:** `is_port_configuration_compliant`

**Steps to reproduce**
```python
from device_posture import is_port_configuration_compliant
is_port_configuration_compliant([], [22])
```

**Expected:** `True` (spec example).
**Actual:** `False`

**Customer impact:** The most locked-down devices are flagged as non-compliant. This is a false red: safe, but it creates noise and erodes trust in the product.

**Root cause:** `any()` of an empty sequence is `False`; `all()` of an empty sequence is `True`. Same root cause as BUG-02.

**Suggested fix:** Same as BUG-02.

---

## BUG-10 – Password check accepts non-string inputs instead of raising TypeError

**Severity:** Medium
**Function:** `is_password_valid`
**Test plan cases:** PW-15 to PW-18

**Steps to reproduce**
```python
from device_posture import is_password_valid
is_password_valid(list("Passw0rd!"))
is_password_valid(set("Passw0rd!"))
is_password_valid(dict.fromkeys("Passw0rd!"))
is_password_valid(b"Passw0rd!")
```

**Expected:** `TypeError` for all four.
**Actual:** `True` for the list, set and dict; `AttributeError` for bytes.

**Customer impact:** Bad data from an upstream integration (for example, a parsed JSON field that is a list) can be reported as a valid password instead of being rejected as an error.

**Root cause:** No explicit type check. `TypeError` is only raised by accident when `len()` fails (e.g. `None`, `int`).

**Suggested fix:** Add `if not isinstance(password, str): raise TypeError(...)` at the top of the function.

---

## BUG-11 – Risk level accepts scores outside 0–100

**Severity:** Low
**Function:** `get_risk_level`

**Steps to reproduce**
```python
from device_posture import get_risk_level
get_risk_level(-1)
get_risk_level(101)
```

**Expected:** `ValueError` for both.
**Actual:** `"LOW"` and `"HIGH"`.

**Customer impact:** Invalid scores from a bug elsewhere are hidden instead of surfacing as errors. Low impact, because `calculate_risk_score` caps scores at 100.

**Suggested fix:** Add `if not 0 <= score <= 100: raise ValueError(...)` at the top of the function.

---

## BUG-12 – `max_attempts < 1` does not raise ValueError

**Severity:** Low
**Function:** `RemediationEngine`

**Steps to reproduce**
```python
from unittest.mock import Mock
from device_posture import RemediationEngine
RemediationEngine(Mock(), max_attempts=0).remediate("dev1", "fix")
```

**Expected:** `ValueError`
**Actual:** `RemediationFailed`, without any attempt.

**Customer impact:** A configuration mistake is reported as a failed fix on the device instead of as a configuration error, which sends troubleshooting in the wrong direction.

**Suggested fix:** Validate in `__init__`: `if max_attempts < 1: raise ValueError(...)`
