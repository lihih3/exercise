"""
Tests for is_port_configuration_compliant.
Tests that expose a bug are expected to FAIL until the bug is fixed (see BUGS.md).
"""
import pytest

from device_posture import is_port_configuration_compliant


# id: (open_ports, allowed_ports, expected)
CASES = {
    "PT-01 all open ports allowed": ([22, 443], [22, 80, 443], True),
    "PT-02 no open port allowed": ([3389], [22, 443], False),
    "PT-03 one allowed one not": ([22, 3389], [22, 443], False),
    "PT-04 bad port first": ([3389, 22], [22, 443], False),
    "PT-05 no open ports": ([], [22], True),
    "PT-06 nothing open nothing allowed": ([], [], True),
    "PT-07 open port with empty allow-list": ([22], [], False),
    "PT-08 duplicate open ports": ([22, 22], [22], True),
}


@pytest.mark.parametrize("open_ports, allowed_ports, expected", CASES.values(), ids=CASES.keys())
def test_port_configuration_compliance(open_ports, allowed_ports, expected):
    assert is_port_configuration_compliant(open_ports, allowed_ports) is expected
