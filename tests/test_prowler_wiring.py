"""Tests for Prowler error-detection logic used in phase_9_cloud_assessment."""


# The error strings the implementation checks to decide whether to skip DB save.
ERROR_STRINGS = ("not installed", "Timeout", "Error", "Tool not found")


def _is_prowler_error(output: str) -> bool:
    """Mirror of the check used in methodology.py."""
    return any(x in output[:50] for x in ERROR_STRINGS)


def test_not_installed_is_detected():
    msg = "Tool not found: prowler"
    assert _is_prowler_error(msg)


def test_timeout_is_detected():
    msg = "Timeout after 600s: prowler aws ..."
    assert _is_prowler_error(msg)


def test_generic_error_is_detected():
    msg = "Error: permission denied"
    assert _is_prowler_error(msg)


def test_valid_output_is_not_detected_as_error():
    msg = "[PASS] S3 bucket encryption enabled\n[FAIL] MFA not enforced on root"
    assert not _is_prowler_error(msg)


def test_empty_output_is_not_detected_as_error():
    # Empty/no output is handled by "no output" string from _run() — not an install error
    msg = "(no output)"
    assert not _is_prowler_error(msg)


def test_error_at_boundary_inside():
    # Error token starts at char 45 — within the [:50] window (just inside)
    msg = "A" * 45 + "Error: something"
    assert _is_prowler_error(msg)


def test_error_beyond_boundary_not_detected():
    # Error token starts at char 51 — outside the [:50] window
    msg = "A" * 51 + "Error: something"
    assert not _is_prowler_error(msg)
