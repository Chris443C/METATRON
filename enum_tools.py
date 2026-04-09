#!/usr/bin/env python3
"""METATRON - enum_tools.py  Phase 3: structured enumeration tools."""
import tools


def run_enum4linux(target):
    """SMB/NetBIOS enumeration. Returns structured dict."""
    raw = tools.run_tool(["enum4linux", "-a", target], timeout=180)
    return {"raw_output": raw, "tool": "enum4linux"}


def run_smb_nmap_scripts(target):
    """SMB enumeration via nmap scripts."""
    raw = tools.run_tool([
        "nmap", "--script",
        "smb-enum-shares,smb-enum-users,smb-vuln-ms17-010",
        target
    ], timeout=120)
    return {"raw_output": raw, "tool": "nmap-smb"}


def run_api_discovery(target):
    """Probe common API and doc paths via HTTP HEAD requests."""
    try:
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except ImportError:
        return {"found_endpoints": [], "raw_output": "requests library not installed", "tool": "api_discovery"}

    base = target if target.startswith("http") else f"http://{target}"
    paths = ["/api", "/api/v1", "/api/v2", "/swagger", "/swagger.json",
             "/openapi.json", "/graphql", "/health", "/docs", "/redoc",
             "/.well-known/openapi.json", "/v1", "/v2"]
    found = []
    for path in paths:
        url = base.rstrip("/") + path
        try:
            r = requests.head(url, timeout=5, allow_redirects=True, verify=False)
            if r.status_code not in (404, 410):
                found.append({"url": url, "status": r.status_code})
        except Exception:
            pass
    raw = "\n".join(f"{e['status']} {e['url']}" for e in found) or "No API endpoints discovered"
    return {"found_endpoints": found, "raw_output": raw, "tool": "api_discovery"}


def run_ldap_enum(target, port=389):
    """Basic LDAP enumeration via nmap scripts."""
    raw = tools.run_tool([
        "nmap", "-p", str(port),
        "--script", "ldap-rootdse,ldap-search",
        target
    ], timeout=60)
    return {"raw_output": raw, "tool": "nmap-ldap"}


def run_web_dir_enum(target, tool="gobuster"):
    """Web directory enumeration dispatcher. Returns structured dict."""
    if tool == "gobuster":
        raw = tools.run_gobuster_dirs(target)
    elif tool == "dirb":
        raw = tools.run_dirb(target)
    elif tool == "ffuf":
        raw = tools.run_ffuf(target)
    else:
        raw = tools.run_gobuster_dirs(target)
    return {"raw_output": raw, "tool_used": tool}


def run_full_enumeration(target, options):
    """
    Orchestrator for Phase 3.
    options: dict with bool keys: web_dirs, smb, ldap, api_discovery
    Returns combined results dict.
    """
    results = {"target": target, "sections": {}}
    if options.get("web_dirs"):
        results["sections"]["web_dirs"] = run_web_dir_enum(target)
    if options.get("smb"):
        results["sections"]["smb"] = run_enum4linux(target)
    if options.get("ldap"):
        results["sections"]["ldap"] = run_ldap_enum(target)
    if options.get("api_discovery"):
        results["sections"]["api"] = run_api_discovery(target)
    return results


def format_enum_for_llm(enum_results):
    """Convert enumeration results dict to flat string for LLM prompt."""
    parts = [f"=== ENUMERATION RESULTS: {enum_results.get('target', 'unknown')} ==="]
    for section_name, section_data in enum_results.get("sections", {}).items():
        parts.append(f"\n--- {section_name.upper()} ---")
        parts.append(section_data.get("raw_output", "No output"))
    return "\n".join(parts)
