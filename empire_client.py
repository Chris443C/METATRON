#!/usr/bin/env python3
"""
METATRON - empire_client.py
PowerShell Empire REST API integration — safe enumeration modules only.

Empire must be running externally: sudo ./empire --rest
Default: http://localhost:1337

SAFE_MODULES whitelist restricts to read-only enumeration.
No persistence, credential dumping, or lateral movement modules are permitted.
"""
import requests
import json

EMPIRE_BASE     = "http://localhost:1337"
EMPIRE_USERNAME = "empireadmin"
EMPIRE_PASSWORD = "password123"  # Change to match your Empire server config

# Whitelist of approved read-only enumeration modules.
# Only modules in this list can be tasked via METATRON.
SAFE_MODULES = {
    "situational_awareness/host/winenum",
    "situational_awareness/host/computerdetails",
    "situational_awareness/host/get_domain_sid",
    "situational_awareness/network/get_spn",
    "situational_awareness/network/portscan",
    "situational_awareness/network/get_sql_server_info",
    "situational_awareness/network/get_rdp_settings",
    "situational_awareness/network/get_domain_controller",
    "situational_awareness/network/bloodhound3",
    "collection/find_interesting_files",
    "collection/get_clipboard",
}


class EmpireClient:
    """Thin REST client for PowerShell Empire BC-Security fork."""

    def __init__(self, base_url=EMPIRE_BASE, username=EMPIRE_USERNAME, password=EMPIRE_PASSWORD):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self._token = None

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        return h

    def login(self):
        """Authenticate with Empire. Returns (ok, message)."""
        try:
            r = requests.post(
                f"{self.base_url}/api/admin/login",
                json={"username": self.username, "password": self.password},
                timeout=10, verify=False
            )
            if r.status_code == 200:
                data = r.json()
                self._token = data.get("token")
                return bool(self._token), (
                    "Empire login OK" if self._token else "Empire login failed: no token"
                )
            return False, f"Empire login failed: HTTP {r.status_code}"
        except requests.exceptions.ConnectionError:
            return False, (
                f"Empire not reachable at {self.base_url}. "
                "Start with: sudo ./empire --rest"
            )
        except Exception as e:
            return False, f"Empire connection error: {e}"

    def list_agents(self):
        """List active Empire agents. Returns list of dicts."""
        try:
            r = requests.get(f"{self.base_url}/api/agents", headers=self._headers(),
                             timeout=10, verify=False)
            return r.json().get("agents", [])
        except Exception as e:
            return [{"error": str(e)}]

    def list_modules(self, filter_safe=True):
        """List available modules, optionally filtered to SAFE_MODULES only."""
        try:
            r = requests.get(f"{self.base_url}/api/modules", headers=self._headers(),
                             timeout=10, verify=False)
            modules = r.json().get("modules", [])
            if filter_safe:
                modules = [m for m in modules if m.get("Name") in SAFE_MODULES]
            return modules
        except Exception as e:
            return [{"error": str(e)}]

    def task_agent(self, agent_name, module_name, options=None):
        """
        Task an agent with a module.
        BLOCKED unless module_name is in SAFE_MODULES whitelist.
        Returns (ok, result_message).
        """
        if module_name not in SAFE_MODULES:
            return False, (
                f"BLOCKED: Module '{module_name}' is not in SAFE_MODULES whitelist.\n"
                f"METATRON restricts Empire to read-only enumeration modules.\n"
                f"Permitted modules: {sorted(SAFE_MODULES)}"
            )
        payload = {"Module": module_name, "Options": options or {}}
        try:
            r = requests.post(
                f"{self.base_url}/api/agents/{agent_name}/tasks/module",
                json=payload,
                headers=self._headers(),
                timeout=10, verify=False
            )
            if r.status_code in (200, 201):
                return True, f"Module tasked: {module_name} on agent {agent_name}"
            return False, f"Task failed: HTTP {r.status_code} — {r.text[:200]}"
        except Exception as e:
            return False, f"Task error: {e}"

    def get_agent_results(self, agent_name, limit=20):
        """Get task results from an agent. Returns list of result dicts."""
        try:
            r = requests.get(
                f"{self.base_url}/api/agents/{agent_name}/task_results",
                headers=self._headers(),
                timeout=10, verify=False
            )
            results = r.json().get("results", [])
            return results[:limit]
        except Exception as e:
            return [{"error": str(e)}]

    def format_results_for_llm(self, agent_name, results):
        """Format Empire agent results as string for LLM analysis."""
        parts = [f"=== EMPIRE AGENT RESULTS: {agent_name} ==="]
        for res in results:
            parts.append(
                f"\n--- Task: {res.get('taskID', '?')} | Module: {res.get('module', '?')} ---"
            )
            output = str(res.get("results", ""))[:2000]
            parts.append(output)
        return "\n".join(parts)


def get_empire_client():
    """Return a logged-in EmpireClient instance or None if unavailable."""
    client = EmpireClient()
    ok, msg = client.login()
    if ok:
        return client
    return None


def empire_availability_check():
    """Check if Empire is running and reachable. Returns (ok, message)."""
    client = EmpireClient()
    ok, msg = client.login()
    return ok, msg
