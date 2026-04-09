#!/usr/bin/env python3
"""METATRON - powershell_tools.py  PowerShell-based cloud and Windows assessment."""
import subprocess
import shutil


def _pwsh_available():
    return shutil.which("pwsh") is not None or shutil.which("powershell") is not None


def _pwsh_binary():
    return "pwsh" if shutil.which("pwsh") else "powershell"


def _run_ps(script, timeout=120):
    """Run a PowerShell script string. Returns stdout+stderr."""
    if not _pwsh_available():
        return "PowerShell (pwsh) not installed. Install: https://aka.ms/pscore6"
    binary = _pwsh_binary()
    try:
        r = subprocess.run(
            [binary, "-NonInteractive", "-NoProfile", "-Command", script],
            capture_output=True, text=True, timeout=timeout
        )
        output = (r.stdout + r.stderr).strip()
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return f"PowerShell timeout after {timeout}s"
    except Exception as e:
        return f"PowerShell error: {e}"


# ─────────────────────────────────────────────
# MODULE AVAILABILITY CHECKS
# ─────────────────────────────────────────────

def check_az_module():
    """Check if Az PowerShell module is installed."""
    out = _run_ps(
        "Get-Module -ListAvailable -Name Az -ErrorAction SilentlyContinue "
        "| Select-Object -ExpandProperty Version"
    )
    if out and "not installed" not in out.lower() and "error" not in out.lower():
        return True, f"Az module version: {out[:50]}"
    return False, "Az PowerShell module not installed. Install: Install-Module Az"


def check_graph_module():
    """Check if Microsoft.Graph module is installed."""
    out = _run_ps(
        "Get-Module -ListAvailable -Name Microsoft.Graph -ErrorAction SilentlyContinue "
        "| Select-Object -First 1 -ExpandProperty Version"
    )
    if out and "error" not in out.lower():
        return True, f"Microsoft.Graph version: {out[:50]}"
    return False, "Microsoft.Graph not installed. Install: Install-Module Microsoft.Graph"


def check_aws_ps_module():
    """Check if AWS Tools for PowerShell module is installed."""
    out = _run_ps(
        "Get-Module -ListAvailable -Name AWSPowerShell.NetCore -ErrorAction SilentlyContinue "
        "| Select-Object -ExpandProperty Version"
    )
    if out and "error" not in out.lower():
        return True, f"AWS PowerShell version: {out[:50]}"
    return False, "AWS PowerShell not installed. Install: Install-Module AWSPowerShell.NetCore"


# ─────────────────────────────────────────────
# AZ POWERSHELL — AZURE ASSESSMENT
# ─────────────────────────────────────────────

def az_get_current_context():
    """Get current Azure subscription context."""
    return _run_ps("Get-AzContext | ConvertTo-Json")


def az_list_subscriptions():
    return _run_ps("Get-AzSubscription | ConvertTo-Json")


def az_list_resources():
    return _run_ps(
        "Get-AzResource | Select-Object Name,ResourceType,Location | ConvertTo-Json"
    )


def az_get_role_assignments():
    return _run_ps(
        "Get-AzRoleAssignment | Select-Object DisplayName,RoleDefinitionName,Scope | ConvertTo-Json",
        timeout=60
    )


def az_list_vms():
    return _run_ps(
        "Get-AzVM | Select-Object Name,Location,"
        "@{N='OS';E={$_.StorageProfile.OsDisk.OsType}} | ConvertTo-Json"
    )


def az_get_security_contacts():
    return _run_ps("Get-AzSecurityContact | ConvertTo-Json -ErrorAction SilentlyContinue")


def az_check_jit_policies():
    return _run_ps("Get-AzJitNetworkAccessPolicy | ConvertTo-Json -ErrorAction SilentlyContinue")


# ─────────────────────────────────────────────
# MICROSOFT GRAPH POWERSHELL — ENTRA ID
# ─────────────────────────────────────────────

def graph_get_users(limit=50):
    return _run_ps(
        f"Get-MgUser -Top {limit} | "
        f"Select-Object DisplayName,UserPrincipalName,AccountEnabled | ConvertTo-Json",
        timeout=60
    )


def graph_get_privileged_roles():
    return _run_ps(
        "Get-MgDirectoryRole | "
        "Where-Object {$_.DisplayName -like '*Admin*' -or $_.DisplayName -like '*Global*'} "
        "| ConvertTo-Json"
    )


def graph_get_app_registrations():
    return _run_ps(
        "Get-MgApplication -Top 50 | "
        "Select-Object DisplayName,AppId,SignInAudience | ConvertTo-Json",
        timeout=60
    )


def graph_get_conditional_access_policies():
    return _run_ps(
        "Get-MgIdentityConditionalAccessPolicy | Select-Object DisplayName,State | ConvertTo-Json"
    )


# ─────────────────────────────────────────────
# AWS POWERSHELL
# ─────────────────────────────────────────────

def aws_ps_get_caller_identity():
    return _run_ps("Get-STSCallerIdentity | ConvertTo-Json")


def aws_ps_list_buckets():
    return _run_ps("Get-S3Bucket | ConvertTo-Json")


def aws_ps_list_iam_users():
    return _run_ps("Get-IAMUserList | ConvertTo-Json", timeout=60)


# ─────────────────────────────────────────────
# TEST-NETCONNECTION — WINDOWS SEGMENTATION
# ─────────────────────────────────────────────

def test_net_connection(target_host, port, timeout_seconds=3):
    """
    Use Test-NetConnection for Windows-native segmentation checking.
    Returns raw output string with TcpTestSucceeded result.
    """
    script = (
        f"$r = Test-NetConnection -ComputerName '{target_host}' "
        f"-Port {port} -WarningAction SilentlyContinue; "
        f"$r | Select-Object ComputerName,RemotePort,TcpTestSucceeded | ConvertTo-Json"
    )
    return _run_ps(script, timeout=timeout_seconds + 5)


def test_net_connection_batch(targets):
    """
    Run Test-NetConnection for a list of target dicts.
    targets: list of dicts with keys: source_label, dest_host, port
    Returns list of result dicts.
    """
    results = []
    for t in targets:
        raw = test_net_connection(t["dest_host"], t["port"])
        success = "True" in raw
        results.append({
            "source_label": t.get("source_label", "tester"),
            "dest_host": t["dest_host"],
            "port": t["port"],
            "result": "FAIL" if success else "PASS",
            "raw_output": raw,
        })
    return results


def format_ps_results_for_llm(module_name, results_dict):
    """Convert PowerShell results to flat string for LLM prompt."""
    parts = [f"=== POWERSHELL ASSESSMENT: {module_name.upper()} ==="]
    for section, output in results_dict.items():
        parts.append(f"\n--- {section.upper().replace('_', ' ')} ---")
        parts.append(str(output)[:2000])
    return "\n".join(parts)
