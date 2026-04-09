"""Tests for Prowler error-detection logic used in phase_9_cloud_assessment."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import cloud_tools

_PROWLER_ERROR_STRINGS = cloud_tools._PROWLER_ERROR_STRINGS


def _is_prowler_error(output: str) -> bool:
    """Check if Prowler output signals a failure condition."""
    return any(x in output[:50] for x in _PROWLER_ERROR_STRINGS)


def test_prowler_not_installed_is_detected():
    # This is the actual message returned by cloud_tools.aws_run_prowler()
    # when shutil.which("prowler") returns None
    msg = "Prowler not installed. Install: pip install prowler"
    assert _is_prowler_error(msg)


def test_tool_not_found_is_detected():
    # This is the message returned by _run() if prowler binary is missing
    # (fallback path)
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
    # "Error: " (7 chars) starts at char 43 — fully within the [:50] window
    msg = "A" * 43 + "Error: something"
    assert _is_prowler_error(msg)


def test_error_beyond_boundary_not_detected():
    # Error token starts at char 51 — outside the [:50] window
    msg = "A" * 51 + "Error: something"
    assert not _is_prowler_error(msg)
