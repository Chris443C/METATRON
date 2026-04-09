#!/usr/bin/env python3
"""METATRON - cloud_tools.py  Cloud assessment wrappers: AWS, Azure, GCP."""
import subprocess
import json
import shutil


def _run(cmd, timeout=120):
    """Run a command, return stdout+stderr as string. Never raises."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout + r.stderr).strip() or "(no output)"
    except FileNotFoundError:
        return f"Tool not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return f"Timeout after {timeout}s: {' '.join(cmd)}"
    except Exception as e:
        return f"Error: {e}"


def _tool_available(name):
    return shutil.which(name) is not None


# ─────────────────────────────────────────────
# CREDENTIAL VALIDATION
# ─────────────────────────────────────────────

def validate_aws_credentials():
    """Check AWS credentials are configured. Returns (ok, message)."""
    if not _tool_available("aws"):
        return False, "aws CLI not installed"
    out = _run(["aws", "sts", "get-caller-identity", "--output", "json"])
    if '"UserId"' in out or '"Account"' in out:
        try:
            data = json.loads(out)
            return True, f"AWS: Account={data.get('Account','?')} ARN={data.get('Arn','?')}"
        except Exception:
            return True, out[:200]
    return False, f"AWS credential check failed: {out[:200]}"


def validate_azure_credentials():
    """Check Azure credentials are configured. Returns (ok, message)."""
    if not _tool_available("az"):
        return False, "az CLI not installed"
    out = _run(["az", "account", "show", "--output", "json"])
    if '"name"' in out or '"id"' in out:
        try:
            data = json.loads(out)
            return True, f"Azure: Sub={data.get('name','?')} ID={data.get('id','?')}"
        except Exception:
            return True, out[:200]
    return False, f"Azure credential check failed: {out[:200]}"


def validate_gcp_credentials():
    """Check GCP credentials are configured. Returns (ok, message)."""
    if not _tool_available("gcloud"):
        return False, "gcloud CLI not installed"
    out = _run(["gcloud", "auth", "list", "--format=json"])
    if '"account"' in out:
        return True, f"GCP credentials found: {out[:200]}"
    return False, f"GCP credential check failed: {out[:200]}"


# ─────────────────────────────────────────────
# AWS ASSESSMENT FUNCTIONS
# ─────────────────────────────────────────────

def aws_get_account_info():
    return _run(["aws", "sts", "get-caller-identity", "--output", "json"])


def aws_list_iam_users():
    return _run(["aws", "iam", "list-users", "--output", "json"], timeout=60)


def aws_get_account_summary():
    return _run(["aws", "iam", "get-account-summary", "--output", "json"])


def aws_list_buckets():
    return _run(["aws", "s3api", "list-buckets", "--output", "json"])


def aws_list_security_groups(region="us-east-1"):
    return _run(["aws", "ec2", "describe-security-groups",
                 "--region", region, "--output", "json"], timeout=60)


def aws_check_cloudtrail():
    return _run(["aws", "cloudtrail", "describe-trails", "--output", "json"])


def aws_list_ec2_instances(region="us-east-1"):
    return _run([
        "aws", "ec2", "describe-instances",
        "--region", region,
        "--query", "Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress,Tags]",
        "--output", "json"
    ], timeout=60)


def aws_run_prowler(output_dir="/tmp/prowler_output"):
    """Run Prowler cloud security assessment if installed."""
    if not _tool_available("prowler"):
        return "Prowler not installed. Install: pip install prowler"
    return _run(["prowler", "aws", "--output-formats", "json",
                 "--output-directory", output_dir, "-M", "json"], timeout=600)


def run_aws_assessment(engagement_id=None):
    """Full AWS assessment. Returns dict of section_name -> raw_output."""
    ok, msg = validate_aws_credentials()
    if not ok:
        return {"error": msg}
    results = {}
    results["account_info"]    = aws_get_account_info()
    results["iam_summary"]     = aws_get_account_summary()
    results["iam_users"]       = aws_list_iam_users()
    results["s3_buckets"]      = aws_list_buckets()
    results["cloudtrail"]      = aws_check_cloudtrail()
    results["security_groups"] = aws_list_security_groups()
    return results


# ─────────────────────────────────────────────
# AZURE ASSESSMENT FUNCTIONS
# ─────────────────────────────────────────────

def azure_get_account_info():
    return _run(["az", "account", "show", "--output", "json"])


def azure_list_subscriptions():
    return _run(["az", "account", "list", "--output", "json"])


def azure_list_resource_groups():
    return _run(["az", "group", "list", "--output", "json"], timeout=60)


def azure_list_vms():
    return _run(["az", "vm", "list", "--output", "json"], timeout=60)


def azure_list_storage_accounts():
    return _run(["az", "storage", "account", "list", "--output", "json"], timeout=60)


def azure_list_network_security_groups():
    return _run(["az", "network", "nsg", "list", "--output", "json"], timeout=60)


def azure_list_role_assignments():
    return _run(["az", "role", "assignment", "list", "--all", "--output", "json"], timeout=120)


def azure_get_defender_assessments():
    return _run(["az", "security", "assessment", "list", "--output", "json"], timeout=120)


def run_azure_assessment():
    """Full Azure assessment. Returns dict of section_name -> raw_output."""
    ok, msg = validate_azure_credentials()
    if not ok:
        return {"error": msg}
    results = {}
    results["account_info"]       = azure_get_account_info()
    results["subscriptions"]      = azure_list_subscriptions()
    results["resource_groups"]    = azure_list_resource_groups()
    results["vms"]                = azure_list_vms()
    results["storage_accounts"]   = azure_list_storage_accounts()
    results["nsgs"]               = azure_list_network_security_groups()
    results["role_assignments"]   = azure_list_role_assignments()
    results["defender_assessments"] = azure_get_defender_assessments()
    return results


# ─────────────────────────────────────────────
# GCP ASSESSMENT FUNCTIONS
# ─────────────────────────────────────────────

def gcp_list_projects():
    return _run(["gcloud", "projects", "list", "--format=json"])


def gcp_list_buckets():
    return _run(["gcloud", "storage", "buckets", "list", "--format=json"], timeout=60)


def gcp_list_compute_instances(project=None):
    cmd = ["gcloud", "compute", "instances", "list", "--format=json"]
    if project:
        cmd += ["--project", project]
    return _run(cmd, timeout=60)


def gcp_list_firewall_rules(project=None):
    cmd = ["gcloud", "compute", "firewall-rules", "list", "--format=json"]
    if project:
        cmd += ["--project", project]
    return _run(cmd, timeout=60)


def gcp_get_scc_findings():
    return _run(["gcloud", "scc", "findings", "list",
                 "--format=json", "--filter=state=ACTIVE"], timeout=120)


def run_gcp_assessment():
    """Full GCP assessment. Returns dict of section_name -> raw_output."""
    ok, msg = validate_gcp_credentials()
    if not ok:
        return {"error": msg}
    results = {}
    results["projects"]          = gcp_list_projects()
    results["buckets"]           = gcp_list_buckets()
    results["compute_instances"] = gcp_list_compute_instances()
    results["firewall_rules"]    = gcp_list_firewall_rules()
    results["scc_findings"]      = gcp_get_scc_findings()
    return results


def format_cloud_results_for_llm(provider, results_dict):
    """Convert cloud assessment results dict to flat string for LLM prompt."""
    parts = [f"=== CLOUD ASSESSMENT: {provider.upper()} ==="]
    if "error" in results_dict:
        return f"CLOUD ASSESSMENT ERROR: {results_dict['error']}"
    for section, output in results_dict.items():
        parts.append(f"\n--- {section.upper().replace('_', ' ')} ---")
        truncated = str(output)[:3000]
        parts.append(truncated)
        if len(str(output)) > 3000:
            parts.append(f"... [{len(str(output)) - 3000} chars truncated]")
    return "\n".join(parts)
