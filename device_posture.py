"""
device_posture.py
=================
Device Posture & Auto-Remediation module (practice exercise).

This module is the "feature under test". The docstring of each function
is the SPEC (the product requirement). The implementation may NOT match
the spec - your job as QA is to find out where.

DO NOT fix the code before you have a failing test that proves the bug.
"""

from datetime import datetime, timedelta


ALLOWED_SPECIAL_CHARS = "!@#$%^&*"


# ---------------------------------------------------------------------------
# 1. Password policy
# ---------------------------------------------------------------------------
def is_password_valid(password: str) -> bool:
    """
    Validates a local-account password against the company security policy.
    A password is VALID only if ALL of the following hold:
      - At least 8 characters long
      - Contains at least one uppercase letter
      - Contains at least one digit
      - Contains at least one special character from: !@#$%^&*
    Returns True if valid, False otherwise.
    Raises TypeError if password is not a string.
    """
    if len(password) < 8:
        return False
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in ALLOWED_SPECIAL_CHARS for c in password)
    if has_upper and has_digit or has_special:
        return True
    return False


# ---------------------------------------------------------------------------
# 2. Firewall / open ports
# ---------------------------------------------------------------------------
def is_port_configuration_compliant(open_ports: list, allowed_ports: list) -> bool:
    """
    A device is COMPLIANT only if EVERY open port appears in allowed_ports.
    A device with no open ports is compliant.

    Examples:
      open_ports=[22, 443],  allowed_ports=[22, 80, 443] -> True
      open_ports=[22, 3389], allowed_ports=[22, 443]     -> False  (RDP not allowed)
      open_ports=[],         allowed_ports=[22]          -> True
    """
    return any(port in allowed_ports for port in open_ports)


# ---------------------------------------------------------------------------
# 3. OS version
# ---------------------------------------------------------------------------
def is_os_version_supported(version: str, min_version: str) -> bool:
    """
    Returns True if the device OS version is >= min_version.
    Versions are dot-separated numbers, e.g. "10.15.7", "14.2", "11".

    Examples:
      is_os_version_supported("14.2", "13.0")   -> True
      is_os_version_supported("12.6", "13.0")   -> False
      is_os_version_supported("13.0", "13.0")   -> True   (equal is supported)
    """
    return version >= min_version


# ---------------------------------------------------------------------------
# 4. Risk score
# ---------------------------------------------------------------------------
SEVERITY_WEIGHTS = {"low": 5, "medium": 15, "high": 30, "critical": 50}


def calculate_risk_score(findings: list) -> int:
    """
    Each finding is a dict: {"id": str, "severity": "low"|"medium"|"high"|"critical"}.
    Score = sum of severity weights, CAPPED at 100.
    Severity is case-insensitive ("HIGH" == "high").
    Unknown severity -> raise ValueError.
    Empty list -> 0.
    """
    score = 0
    for finding in findings:
        severity = finding["severity"]
        if severity not in SEVERITY_WEIGHTS:
            raise ValueError(f"Unknown severity: {severity}")
        score += SEVERITY_WEIGHTS[severity]
    return min(score, 100)


def get_risk_level(score: int) -> str:
    """
    Maps a risk score to a level:
       0 - 39  -> "LOW"
      40 - 69  -> "MEDIUM"
      70 - 100 -> "HIGH"
    Score outside 0..100 -> raise ValueError.
    """
    if score > 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


# ---------------------------------------------------------------------------
# 5. Scan freshness
# ---------------------------------------------------------------------------
STALE_AFTER = timedelta(hours=24)


def is_scan_stale(last_scan_time: datetime, now: datetime = None) -> bool:
    """
    A posture scan is STALE if more than 24 hours have passed since it ran.
    Exactly 24 hours is NOT stale.
    `now` is optional; defaults to the current time.
    """
    if now is None:
        now = datetime.now()
    elapsed = now - last_scan_time
    return elapsed.seconds > STALE_AFTER.total_seconds()


# ---------------------------------------------------------------------------
# 6. Auto-remediation engine
# ---------------------------------------------------------------------------
class RemediationFailed(Exception):
    pass


class RemediationEngine:
    """
    Applies a fix to a non-compliant device using an injected `executor`.

    executor must expose:
      executor.apply(device_id, fix_name) -> bool   (True = success)
      executor.rollback(device_id, fix_name) -> None

    SPEC:
      - Try to apply the fix. If it fails, retry until a total of
        `max_attempts` attempts were made (default 3).
      - Return the number of attempts it took on success.
      - If all attempts fail: call executor.rollback(device_id, fix_name)
        EXACTLY once, then raise RemediationFailed.
      - max_attempts < 1 -> raise ValueError.
    """

    def __init__(self, executor, max_attempts: int = 3):
        self.executor = executor
        self.max_attempts = max_attempts

    def remediate(self, device_id: str, fix_name: str) -> int:
        for attempt in range(1, self.max_attempts):
            if self.executor.apply(device_id, fix_name):
                return attempt
        raise RemediationFailed(f"{fix_name} failed on {device_id}")
