"""
Tests for is_os_version_supported.
Tests that expose a bug are expected to FAIL until the bug is fixed (see BUGS.md).
"""
import pytest

from device_posture import is_os_version_supported


# id: (version, min_version, expected)
CASES = {
    # Examples from the spec
    "OS-01 newer major": ("14.2", "13.0", True),
    "OS-02 older major": ("12.6", "13.0", False),
    "OS-03 equal is supported": ("13.0", "13.0", True),
    # Different number of digits: string comparison breaks here
    "OS-04 one-digit major older": ("9.0", "13.0", False),
    "OS-05 two-digit major newer": ("10.0", "9.0", True),
    "OS-06 two-digit minor newer": ("13.10", "13.9", True),
    "OS-07 single-part versions": ("11", "9", True),
    # Different number of parts
    "OS-08 patch above minimum": ("13.0.1", "13.0", True),
    "OS-09 just below minimum": ("12.9.9", "13.0", False),
    # Major decides even when minor is smaller
    "OS-10 newer major smaller minor": ("14.0", "13.9", True),
}


@pytest.mark.parametrize("version, min_version, expected", CASES.values(), ids=CASES.keys())
def test_os_version_supported(version, min_version, expected):
    assert is_os_version_supported(version, min_version) is expected
