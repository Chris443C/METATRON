#!/usr/bin/env python3
"""METATRON - segmentation_tools.py  PCI DSS 11.4.5 segmentation testing via ncat."""
import subprocess
import socket
import shutil
import time
from datetime import datetime


def _tool_available(name):
    return shutil.which(name) is not None


def _tcp_test_ncat(dest_host, dest_port, timeout=5):
    """
    Test TCP connectivity using ncat --zero-i-o.
    Returns (success: bool|None, raw_output: str, tool_used: str)
    None means tool not available.
    """
    cmd = ["ncat", "--zero-i-o", "--wait", str(timeout), str(dest_host), str(dest_port)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
        connected = r.returncode == 0
        raw = f"ncat exit={r.returncode} stdout={r.stdout.strip()} stderr={r.stderr.strip()}"
        return connected, raw, "ncat"
    except FileNotFoundError:
        return None, "ncat not found", "ncat"
    except subprocess.TimeoutExpired:
        return False, f"ncat timeout after {timeout}s", "ncat"
    except Exception as e:
        return None, f"ncat error: {e}", "ncat"


def _tcp_test_nc(dest_host, dest_port, timeout=5):
    """
    Fallback: test TCP connectivity using nc -z (zero-I/O mode).
    Returns (success: bool|None, raw_output: str, tool_used: str)
    """
    cmd = ["nc", "-z", "-w", str(timeout), str(dest_host), str(dest_port)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
        connected = r.returncode == 0
        raw = f"nc exit={r.returncode} stdout={r.stdout.strip()} stderr={r.stderr.strip()}"
        return connected, raw, "nc"
    except FileNotFoundError:
        return None, "nc not found", "nc"
    except Exception as e:
        return None, f"nc error: {e}", "nc"


def _tcp_test_socket(dest_host, dest_port, timeout=5):
    """
    Last-resort fallback: raw Python socket connect test.
    Returns (success: bool, raw_output: str, tool_used: str)
    """
    start = time.time()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((str(dest_host), int(dest_port)))
        s.close()
        elapsed = time.time() - start
        return True, f"Python socket: connected in {elapsed:.2f}s", "python_socket"
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        elapsed = time.time() - start
        return False, f"Python socket: {type(e).__name__} after {elapsed:.2f}s", "python_socket"
    except Exception as e:
        return False, f"Python socket error: {e}", "python_socket"


def test_connectivity(dest_host, dest_port, protocol="tcp", timeout=5):
    """
    Test connectivity using ncat → nc → Python socket fallback chain.
    Returns dict: {connected, raw_output, tool_used}
    """
    if protocol == "tcp":
        result, raw, tool = _tcp_test_ncat(dest_host, dest_port, timeout)
        if result is None:
            result, raw, tool = _tcp_test_nc(dest_host, dest_port, timeout)
        if result is None:
            result, raw, tool = _tcp_test_socket(dest_host, dest_port, timeout)
    else:
        # UDP: ncat only
        cmd = ["ncat", "-u", "--zero-i-o", "--wait", str(timeout),
               str(dest_host), str(dest_port)]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
            result = r.returncode == 0
            raw = f"ncat UDP exit={r.returncode}"
            tool = "ncat"
        except FileNotFoundError:
            result = False
            raw = "ncat not found — UDP test requires ncat"
            tool = "ncat"
        except Exception as e:
            result = False
            raw = f"UDP test error: {e}"
            tool = "ncat"
    return {"connected": bool(result), "raw_output": raw, "tool_used": tool}


def run_segmentation_test(source_label, dest_host, dest_port, expected,
                          protocol="tcp", timeout=5, tester_name=None):
    """
    Run a single segmentation test and determine PASS/FAIL.

    PASS = result matches expected:
      - expected='blocked' and connected=False → PASS (segmentation working)
      - expected='allowed' and connected=True  → PASS (allowed path confirmed)
    FAIL = result does not match expected
    """
    test_result = test_connectivity(dest_host, dest_port, protocol, timeout)
    connected = test_result["connected"]
    if expected == "blocked":
        pci_result = "PASS" if not connected else "FAIL"
    else:
        pci_result = "PASS" if connected else "FAIL"
    return {
        "source_host": source_label,
        "dest_host": dest_host,
        "dest_port": int(dest_port),
        "protocol": protocol,
        "expected": expected,
        "result": pci_result,
        "connected": connected,
        "tool_used": test_result["tool_used"],
        "raw_output": test_result["raw_output"],
        "tester_name": tester_name or "METATRON",
        "tested_at": datetime.now().isoformat(),
    }


def run_segmentation_suite(test_cases, tester_name=None):
    """
    Run a batch of segmentation tests.
    test_cases: list of dicts with keys: source_label, dest_host, dest_port, expected
                optional: protocol (default 'tcp'), timeout (default 5)
    Returns list of result dicts.
    """
    results = []
    for tc in test_cases:
        result = run_segmentation_test(
            source_label=tc.get("source_label", "tester"),
            dest_host=tc["dest_host"],
            dest_port=tc["dest_port"],
            expected=tc.get("expected", "blocked"),
            protocol=tc.get("protocol", "tcp"),
            timeout=tc.get("timeout", 5),
            tester_name=tester_name,
        )
        results.append(result)
    return results


def format_pci_evidence_table(test_results):
    """
    Format test results as a PCI DSS 11.4.5 evidence table string.
    Suitable for inclusion in reports and LLM analysis.
    """
    header = (
        f"{'SOURCE':<25} {'DESTINATION':<25} {'PORT':<8} {'PROTO':<6} "
        f"{'EXPECTED':<10} {'RESULT':<8} {'TOOL':<15} {'TESTED AT'}"
    )
    separator = "-" * len(header)
    lines = [
        "PCI DSS REQUIREMENT 11.4.5 — SEGMENTATION TEST EVIDENCE",
        separator,
        header,
        separator,
    ]
    pass_count = 0
    fail_count = 0
    for r in test_results:
        status = r["result"]
        if status == "PASS":
            pass_count += 1
        else:
            fail_count += 1
        lines.append(
            f"{r['source_host']:<25} {r['dest_host']:<25} {r['dest_port']:<8} "
            f"{r['protocol']:<6} {r['expected']:<10} {status:<8} "
            f"{r['tool_used']:<15} {r['tested_at'][:19]}"
        )
    lines += [
        separator,
        f"TOTAL: {len(test_results)} tests | PASS: {pass_count} | FAIL: {fail_count}",
        (
            "COMPLIANCE: PASS — all segmentation controls verified"
            if fail_count == 0
            else f"COMPLIANCE: FAIL — {fail_count} segmentation failure(s) detected"
        ),
        f"TESTER: {test_results[0]['tester_name'] if test_results else 'unknown'}",
        "TOOL CHAIN: ncat → nc → python_socket (auto-selected)",
    ]
    return "\n".join(lines)


def interactive_segmentation_wizard(engagement_id=None):
    """
    Interactive wizard to build and run a segmentation test suite.
    Returns (test_results, evidence_table_string).
    """
    from metatron import prompt, success, warn, info, divider
    divider()
    info("PCI DSS 11.4.5 — SEGMENTATION TESTING WIZARD")
    info("Tests connectivity between network segments.")
    info("PASS = connection blocked as expected | FAIL = unexpected connectivity")
    divider()
    tester_name = prompt("Tester name (for chain of custody): ")
    test_cases = []
    print("\n  Enter test cases. Type 'done' for source to finish.\n")
    while True:
        source = input("  Source segment label (e.g. 'Corporate LAN') or 'done': ").strip()
        if source.lower() == "done":
            break
        dest_host = prompt("  Destination IP/hostname: ")
        try:
            dest_port = int(prompt("  Destination port: "))
        except ValueError:
            warn("Invalid port, skipping.")
            continue
        print("  Expected result: [1] Blocked (should fail - typical for CDE isolation)")
        print("                   [2] Allowed (should succeed - for approved paths)")
        expected = "blocked" if input("  [1/2]: ").strip() != "2" else "allowed"
        protocol = "tcp"
        if input("  Protocol TCP? [Y/n]: ").strip().lower() == "n":
            protocol = "udp"
        test_cases.append({
            "source_label": source,
            "dest_host": dest_host,
            "dest_port": dest_port,
            "expected": expected,
            "protocol": protocol,
        })
        success(f"Test case added: {source} → {dest_host}:{dest_port} [{expected}]")
    if not test_cases:
        warn("No test cases entered.")
        return [], ""
    info(f"\nRunning {len(test_cases)} segmentation test(s)...")
    results = run_segmentation_suite(test_cases, tester_name)
    table = format_pci_evidence_table(results)
    print("\n" + table)
    return results, table
