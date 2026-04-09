#!/usr/bin/env python3
"""
METATRON - llm.py
Ollama interface for metatron-qwen model.
Builds prompts, handles AI responses, runs tool dispatch loop.
Model: metatron-qwen (fine-tuned from huihui_ai/qwen3.5-abliterated:9b)
"""

import re
import requests
import json
from tools import run_tool_by_command, run_nmap, run_curl_headers
from search import handle_search_dispatch

OLLAMA_URL  = "http://localhost:11434/api/generate"
MODEL_NAME  = "metatron-qwen"
MAX_TOKENS  = 4096
MAX_TOOL_LOOPS = 9   # max times AI can call tools per session
OLLAMA_TIMEOUT = 600 

# ─────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are METATRON, an elite AI penetration testing assistant running on Parrot OS.
You are precise, technical, and direct. No fluff.

You have access to real tools. To use them, write tags in your response:

  [TOOL: nmap -sV 192.168.1.1]       → runs nmap or any CLI tool
  [SEARCH: CVE-2021-44228 exploit]   → searches the web via DuckDuckGo

Rules:
- Always analyze scan data thoroughly before suggesting exploits
- List vulnerabilities with: name, severity (critical/high/medium/low), port, service
- For each vulnerability, suggest a concrete fix
- If you need more information, use [SEARCH:] or [TOOL:]
- Format vulnerabilities clearly so they can be saved to a database
- Be specific about CVE IDs when you know them
- Always give a final risk rating: CRITICAL / HIGH / MEDIUM / LOW

Output format for vulnerabilities (use this exactly):
VULN: <name> | SEVERITY: <level> | PORT: <port> | SERVICE: <service>
DESC: <description>
FIX: <fix recommendation>

Output format for exploits:
EXPLOIT: <name> | TOOL: <tool> | PAYLOAD: <payload or description>
RESULT: <expected result>
NOTES: <any notes>

End your analysis with:
RISK_LEVEL: <CRITICAL|HIGH|MEDIUM|LOW>
SUMMARY: <2-3 sentence overall summary>
"""


# ─────────────────────────────────────────────
# OLLAMA API CALL
# ─────────────────────────────────────────────

def ask_ollama(prompt: str, context: list = None) -> str:
    """
    Send a prompt to metatron-qwen via Ollama API.
    context: list of previous message dicts for multi-turn conversation.
    Returns the AI response string.
    """
    try:
        payload = {
            "model":  MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": MAX_TOKENS,
                "temperature": 0.7,
                "top_p": 0.9,
            }
        }

        print(f"\n[*] Sending to {MODEL_NAME}...")
        resp = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
        resp.raise_for_status()

        data = resp.json()
        response = data.get("response", "").strip()

        if not response:
            return "[!] Model returned empty response."

        return response

    except requests.exceptions.ConnectionError:
        return "[!] Cannot connect to Ollama. Is it running? Try: ollama serve"
    except requests.exceptions.Timeout:
        return "[!] Ollama timed out. Model may be loading, try again."
    except requests.exceptions.HTTPError as e:
        return f"[!] Ollama HTTP error: {e}"
    except Exception as e:
        return f"[!] Unexpected error: {e}"


# ─────────────────────────────────────────────
# TOOL DISPATCH
# ─────────────────────────────────────────────

def extract_tool_calls(response: str) -> list:
    """
    Extract all [TOOL: ...] and [SEARCH: ...] tags from AI response.
    Returns list of tuples: [("TOOL", "nmap -sV x.x.x.x"), ("SEARCH", "CVE...")]
    """
    calls = []

    tool_matches   = re.findall(r'\[TOOL:\s*(.+?)\]',   response)
    search_matches = re.findall(r'\[SEARCH:\s*(.+?)\]', response)

    for m in tool_matches:
        calls.append(("TOOL", m.strip()))
    for m in search_matches:
        calls.append(("SEARCH", m.strip()))

    return calls


def run_tool_calls(calls: list) -> str:
    """
    Execute all tool/search calls and return combined results string.
    User is prompted [y/N] before each dispatch — default is no.
    """
    if not calls:
        return ""

    results = ""
    for call_type, call_content in calls:
        print(f"\n  [AI REQUEST] {call_type}: {call_content}")
        answer = input("  Run this? [y/N]: ").strip().lower()
        if answer != "y":
            print(f"  [SKIPPED]")
            results += f"\n[{call_type} SKIPPED by user: {call_content}]\n"
            continue

        if call_type == "TOOL":
            output = run_tool_by_command(call_content)
        elif call_type == "SEARCH":
            output = handle_search_dispatch(call_content)
        else:
            output = f"[!] Unknown call type: {call_type}"

        results += f"\n[{call_type} RESULT: {call_content}]\n"
        results += "─" * 40 + "\n"
        results += output.strip() + "\n"

    return results


# ─────────────────────────────────────────────
# PARSER — extract structured data from AI output
# ─────────────────────────────────────────────

def parse_vulnerabilities(response: str) -> list:
    """
    Parse VULN: lines from AI response into dicts.
    Returns list of vulnerability dicts ready for db.save_vulnerability()
    """
    vulns = []
    lines = response.splitlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("VULN:"):
            vuln = {
                "vuln_name":   "",
                "severity":    "medium",
                "port":        "",
                "service":     "",
                "description": "",
                "fix":         ""
            }

            # parse header line: VULN: name | SEVERITY: x | PORT: x | SERVICE: x
            parts = line.split("|")
            for part in parts:
                part = part.strip()
                if part.startswith("VULN:"):
                    vuln["vuln_name"] = part.replace("VULN:", "").strip()
                elif part.startswith("SEVERITY:"):
                    vuln["severity"] = part.replace("SEVERITY:", "").strip().lower()
                elif part.startswith("PORT:"):
                    vuln["port"] = part.replace("PORT:", "").strip()
                elif part.startswith("SERVICE:"):
                    vuln["service"] = part.replace("SERVICE:", "").strip()

            # look ahead for DESC: and FIX: lines
            j = i + 1
            while j < len(lines) and j <= i + 5:
                next_line = lines[j].strip()
                if next_line.startswith("DESC:"):
                    vuln["description"] = next_line.replace("DESC:", "").strip()
                elif next_line.startswith("FIX:"):
                    vuln["fix"] = next_line.replace("FIX:", "").strip()
                j += 1

            if vuln["vuln_name"]:
                vulns.append(vuln)

        i += 1

    return vulns


def parse_exploits(response: str) -> list:
    """
    Parse EXPLOIT: lines from AI response into dicts.
    Returns list of exploit dicts ready for db.save_exploit()
    """
    exploits = []
    lines = response.splitlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("EXPLOIT:"):
            exploit = {
                "exploit_name": "",
                "tool_used":    "",
                "payload":      "",
                "result":       "unknown",
                "notes":        ""
            }

            parts = line.split("|")
            for part in parts:
                part = part.strip()
                if part.startswith("EXPLOIT:"):
                    exploit["exploit_name"] = part.replace("EXPLOIT:", "").strip()
                elif part.startswith("TOOL:"):
                    exploit["tool_used"] = part.replace("TOOL:", "").strip()
                elif part.startswith("PAYLOAD:"):
                    exploit["payload"] = part.replace("PAYLOAD:", "").strip()

            j = i + 1
            while j < len(lines) and j <= i + 4:
                next_line = lines[j].strip()
                if next_line.startswith("RESULT:"):
                    exploit["result"] = next_line.replace("RESULT:", "").strip()
                elif next_line.startswith("NOTES:"):
                    exploit["notes"] = next_line.replace("NOTES:", "").strip()
                j += 1

            if exploit["exploit_name"]:
                exploits.append(exploit)

        i += 1

    return exploits


def parse_risk_level(response: str) -> str:
    """Extract RISK_LEVEL from AI response."""
    match = re.search(r'RISK_LEVEL:\s*(CRITICAL|HIGH|MEDIUM|LOW)', response, re.IGNORECASE)
    return match.group(1).upper() if match else "UNKNOWN"


def parse_summary(response: str) -> str:
    """Extract SUMMARY line from AI response."""
    match = re.search(r'SUMMARY:\s*(.+)', response, re.IGNORECASE)
    return match.group(1).strip() if match else response[:500]


# ─────────────────────────────────────────────
# MAIN ANALYSIS FUNCTION
# ─────────────────────────────────────────────

def analyse_target(target: str, raw_scan: str) -> dict:
    """
    Full analysis pipeline:
    1. Build initial prompt with scan data
    2. Send to metatron-qwen
    3. Run tool dispatch loop if AI requests tools
    4. Parse structured output
    5. Return everything ready for db.py to save

    Returns dict with:
      - full_response   : complete AI text
      - vulnerabilities : list of parsed vuln dicts
      - exploits        : list of parsed exploit dicts
      - risk_level      : CRITICAL/HIGH/MEDIUM/LOW
      - summary         : short summary text
      - raw_scan        : original scan dump
    """

    # ── Step 1: initial prompt ──────────────────
    initial_prompt = f"""{SYSTEM_PROMPT}

TARGET: {target}

RECON DATA:
{raw_scan}

Analyze this target completely. Use [TOOL:] or [SEARCH:] if you need more information.
List all vulnerabilities, fixes, and suggest exploits where applicable.
"""

    full_conversation = initial_prompt
    final_response    = ""

    # ── Step 2: tool dispatch loop ──────────────
    for loop in range(MAX_TOOL_LOOPS):
        response = ask_ollama(full_conversation)

        print(f"\n{'─'*60}")
        print(f"[METATRON - Round {loop + 1}]")
        print(f"{'─'*60}")
        print(response)

        final_response = response

        # check for tool calls
        tool_calls = extract_tool_calls(response)
        if not tool_calls:
            print("\n[*] No tool calls. Analysis complete.")
            break

        # run all tool calls
        tool_results = run_tool_calls(tool_calls)

        # feed results back into conversation
        full_conversation = (
            f"{full_conversation}\n\n"
            f"[YOUR PREVIOUS RESPONSE]\n{response}\n\n"
            f"[TOOL RESULTS]\n{tool_results}\n\n"
            f"Continue your analysis with this new information. "
            f"If analysis is complete, give the final RISK_LEVEL and SUMMARY."
        )

    # ── Step 3: parse structured output ─────────
    vulnerabilities = parse_vulnerabilities(final_response)
    exploits        = parse_exploits(final_response)
    risk_level      = parse_risk_level(final_response)
    summary         = parse_summary(final_response)

    print(f"\n[+] Parsed: {len(vulnerabilities)} vulns, {len(exploits)} exploits | Risk: {risk_level}")

    return {
        "full_response":   final_response,
        "vulnerabilities": vulnerabilities,
        "exploits":        exploits,
        "risk_level":      risk_level,
        "summary":         summary,
        "raw_scan":        raw_scan
    }


# ─────────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("[ llm.py test — direct AI query ]\n")

    # test if ollama is reachable
    try:
        r = requests.get("http://localhost:11434", timeout=5)
        print("[+] Ollama is running.")
    except Exception:
        print("[!] Ollama not reachable. Run: ollama serve")
        exit(1)

    target = input("Test target: ").strip()
    test_scan = f"Test recon for {target} — nmap and whois data would appear here."
    result = analyse_target(target, test_scan)

    print(f"\nRisk Level : {result['risk_level']}")
    print(f"Summary    : {result['summary']}")
    print(f"Vulns found: {len(result['vulnerabilities'])}")
    print(f"Exploits   : {len(result['exploits'])}")


# ─────────────────────────────────────────────
# PHASE-SPECIFIC SYSTEM PROMPTS
# ─────────────────────────────────────────────

RECON_SYSTEM_PROMPT = """You are METATRON, an elite AI penetration testing assistant.
You are in Phase 2: Reconnaissance.
Analyze the recon data and identify the attack surface.
Use [TOOL:] and [SEARCH:] tags to request more information.

Format findings as:
RECON_FINDING: <finding> | TYPE: <port|service|tech|exposure> | INTEREST: <high|medium|low>
RECON_NOTE: <observation needing follow-up in enumeration phase>
End with: RECON_COMPLETE: <brief attack surface summary>"""

ENUM_SYSTEM_PROMPT = """You are METATRON, an elite AI penetration testing assistant.
You are in Phase 3: Enumeration.
Analyze combined recon and enumeration data to map the attack surface.

Format findings as:
ENUM_FINDING: <what was found> | LOCATION: <url/path/share/endpoint> | INTEREST: <high|medium|low>
ATTACK_VECTOR: <potential attack vector> | FINDING: <what enables it>
End with: ENUM_COMPLETE: <top 3 priorities for vulnerability analysis>"""

VULN_ANALYSIS_SYSTEM_PROMPT = """You are METATRON, an elite AI penetration testing assistant.
You are in Phase 4: Vulnerability Analysis.
Validate findings, filter false positives, chain vulnerabilities into attack paths.
Assign CVSS scores (0.0-10.0 based on AV/AC/PR/UI/S/C/I/A).

Use existing VULN:/DESC:/FIX: format plus:
CVSS_SCORE: <0.0-10.0>
FALSE_POSITIVE: NO

Format attack paths as:
ATTACK_PATH: <name>
STEP_1: <first step>
STEP_N: <final step>
PATH_SEVERITY: <CRITICAL|HIGH|MEDIUM|LOW>
PATH_NARRATIVE: <2-3 sentence plain-English description>

End with RISK_LEVEL: and SUMMARY:"""

EXPLOITATION_SYSTEM_PROMPT = """You are METATRON, an elite AI penetration testing assistant.
You are in Phase 5: Exploitation Planning.
Provide step-by-step exploitation guidance. The human operator executes — you plan only.

Format as:
EXPLOIT_PLAN: <vulnerability name>
TOOL: <tool>
COMMAND: <exact command or payload>
EXPECTED_RESULT: <what success looks like>
PRECONDITION: <what must be true>
NOISE_LEVEL: <silent|low|medium|high>
NOTES: <warnings or context>"""

POST_EXPLOIT_SYSTEM_PROMPT = """You are METATRON, an elite AI penetration testing assistant.
You are in Phase 6: Post-Exploitation Analysis.
Suggest techniques to assess impact after initial compromise.
Frame everything in terms of business impact.

Format as:
POST_EXPLOIT_TECHNIQUE: <technique> | TYPE: <privesc|lateral_movement|persistence|data_access>
FROM: <current access level/host> | TO: <target access/host>
METHOD: <how to do it>
IMPACT: <business impact if successful>
EVIDENCE_NEEDED: <what to capture as proof>"""

EXECUTIVE_SUMMARY_PROMPT = """You are METATRON, an elite AI penetration testing assistant.
Generate a professional executive summary for a penetration test report.
No technical jargon in the first paragraph.

Format:
EXEC_SUMMARY_START
<paragraph 1 — what was done, non-technical>
<paragraph 2 — what was found at business level>
<paragraph 3 — top 3 recommendations in plain language>
<paragraph 4 — overall risk verdict>
EXEC_SUMMARY_END"""

RETEST_COMPARISON_PROMPT = """You are METATRON, an elite AI penetration testing assistant.
Compare original pentest findings with retest findings.

For each original vulnerability, output:
RETEST_FINDING: <vuln name> | ORIGINAL_SEVERITY: <level> | STATUS: <FIXED|PARTIAL|NOT_FIXED|NOT_TESTED>
RETEST_NOTE: <explanation>

For new findings: NEW_FINDING: (use standard VULN: format)

End with:
REMEDIATION_SCORE: <0-100>
RETEST_SUMMARY: <2-3 sentence overall assessment>"""

CLOUD_AWS_PROMPT = """You are METATRON, an elite AI penetration testing assistant.
You are in Phase 9: Cloud Assessment — AWS.
Analyze AWS IAM, S3, EC2, security group, and CloudTrail data for security misconfigurations.

Format findings as:
CLOUD_FINDING: <what was found> | PROVIDER: aws | SERVICE: <iam|s3|ec2|cloudtrail|vpc>
SEVERITY: <critical|high|medium|low|info> | RESOURCE: <resource id or name>
DESCRIPTION: <what the issue is>
RECOMMENDATION: <how to fix it>

Rate attack path risk with:
CLOUD_RISK: <critical|high|medium|low>
CLOUD_SUMMARY: <2-3 sentence assessment>"""

CLOUD_AZURE_PROMPT = """You are METATRON, an elite AI penetration testing assistant.
You are in Phase 9: Cloud Assessment — Azure.
Analyze Azure role assignments, NSGs, VMs, storage accounts, and Defender posture.

Format findings as:
CLOUD_FINDING: <what was found> | PROVIDER: azure | SERVICE: <iam|storage|compute|network|defender>
SEVERITY: <critical|high|medium|low|info> | RESOURCE: <resource name>
DESCRIPTION: <what the issue is>
RECOMMENDATION: <how to fix it>

End with:
CLOUD_RISK: <critical|high|medium|low>
CLOUD_SUMMARY: <2-3 sentence assessment>"""

CLOUD_GCP_PROMPT = """You are METATRON, an elite AI penetration testing assistant.
You are in Phase 9: Cloud Assessment — GCP.
Analyze GCP IAM bindings, firewall rules, storage buckets, and Security Command Center findings.

Format findings as:
CLOUD_FINDING: <what was found> | PROVIDER: gcp | SERVICE: <iam|storage|compute|network|scc>
SEVERITY: <critical|high|medium|low|info> | RESOURCE: <resource name>
DESCRIPTION: <what the issue is>
RECOMMENDATION: <how to fix it>

End with:
CLOUD_RISK: <critical|high|medium|low>
CLOUD_SUMMARY: <2-3 sentence assessment>"""

SEGMENTATION_ANALYSIS_PROMPT = """You are METATRON, an elite AI penetration testing assistant.
You are in Phase 10: Segmentation Testing — PCI DSS Requirement 11.4.5.
Analyze ncat/nc connectivity test results and determine segmentation compliance.

For each test result, output:
SEG_RESULT: <source> → <dest>:<port> | STATUS: <PASS|FAIL> | EXPECTED: <blocked|allowed>
SEG_FINDING: <what this means for PCI DSS compliance>
SEG_SEVERITY: <critical|high|medium|low>

Failures where expected=blocked and actual=allowed are PCI DSS violations.

End with:
SEG_COMPLIANT: <YES|NO|PARTIAL>
SEG_NARRATIVE: <2-3 sentence PCI 11.4.5 compliance narrative for the report>
PCI_REQUIREMENT: 11.4.5"""

EMPIRE_ANALYSIS_PROMPT = """You are METATRON, an elite AI penetration testing assistant.
You are reviewing PowerShell Empire enumeration output from an authorised engagement.
Analyze domain users, admin sessions, network topology, and privilege levels.

Format findings as:
EMPIRE_FINDING: <what was found> | TYPE: <user|host|privilege|network|credential_ref>
RISK: <high|medium|low>
LATERAL_PATH: <potential pivot path, if any>
IMPACT: <business impact>

End with:
EMPIRE_SUMMARY: <attack path assessment based on Empire data>
NOTE: All findings are from authorised testing within defined scope."""

PHASE_PROMPTS = {
    2: RECON_SYSTEM_PROMPT,
    3: ENUM_SYSTEM_PROMPT,
    4: VULN_ANALYSIS_SYSTEM_PROMPT,
    5: EXPLOITATION_SYSTEM_PROMPT,
    6: POST_EXPLOIT_SYSTEM_PROMPT,
}

CLOUD_PHASE_PROMPTS = {
    "aws":   CLOUD_AWS_PROMPT,
    "azure": CLOUD_AZURE_PROMPT,
    "gcp":   CLOUD_GCP_PROMPT,
}


# ─────────────────────────────────────────────
# PHASE-SPECIFIC ANALYSIS FUNCTIONS
# ─────────────────────────────────────────────

def build_engagement_context_string(engagement_id):
    """Build scope summary string to prepend to every phase prompt."""
    import db
    e = db.get_engagement(engagement_id)
    if not e:
        return ""
    scope = db.get_scope_items(engagement_id)
    in_s = ", ".join(i["target"] for i in scope["in_scope"]) or "not defined"
    out_s = ", ".join(i["target"] for i in scope["out_of_scope"]) or "none"
    return (f"ENGAGEMENT: {e['engagement_name']}\n"
            f"CLIENT: {e['client_name']}\n"
            f"TEST_TYPE: {e['test_type']} box\n"
            f"IN_SCOPE: {in_s}\n"
            f"OUT_OF_SCOPE: {out_s}\n\n")


def analyse_phase(target, scan_data, phase, engagement_id=None):
    """
    Phase-aware analysis using the correct system prompt.
    Returns same structure as analyse_target() plus phase-specific keys.
    """
    system_prompt = PHASE_PROMPTS.get(phase, SYSTEM_PROMPT)
    context_str = build_engagement_context_string(engagement_id) if engagement_id else ""
    full_prompt = (f"{system_prompt}\n\n{context_str}"
                   f"TARGET: {target}\n\nSCAN DATA:\n{scan_data}")
    conversation = full_prompt
    for _ in range(MAX_TOOL_LOOPS):
        response = ask_ollama(conversation)
        calls = extract_tool_calls(response)
        if not calls:
            break
        tool_results = run_tool_calls(calls)
        conversation += f"\n\n[TOOL RESULTS]\n{tool_results}\n\nContinue analysis:"
    vulns = parse_vulnerabilities(response)
    exploits = parse_exploits(response)
    risk = parse_risk_level(response)
    summary = parse_summary(response)
    attack_paths = parse_attack_paths(response)
    return {
        "full_response": response,
        "vulnerabilities": vulns,
        "exploits": exploits,
        "risk_level": risk,
        "summary": summary,
        "attack_paths": attack_paths,
        "raw_scan": scan_data,
        "phase": phase,
    }


def parse_attack_paths(response):
    """Parse ATTACK_PATH: blocks from LLM response."""
    paths = []
    blocks = re.split(r'ATTACK_PATH:\s*', response)
    for block in blocks[1:]:
        lines = block.strip().split('\n')
        path_name = lines[0].strip()
        steps = []
        severity = "high"
        narrative = ""
        for line in lines[1:]:
            if re.match(r'STEP_\d+:', line):
                steps.append(re.sub(r'^STEP_\d+:\s*', '', line).strip())
            elif line.startswith("PATH_SEVERITY:"):
                severity = re.sub(r'^PATH_SEVERITY:\s*', '', line).strip().lower()
            elif line.startswith("PATH_NARRATIVE:"):
                narrative = re.sub(r'^PATH_NARRATIVE:\s*', '', line).strip()
        if path_name:
            paths.append({"path_name": path_name, "steps": steps,
                          "severity": severity, "narrative": narrative})
    return paths


def generate_executive_summary(engagement_data):
    """Generate executive summary. Returns text between EXEC_SUMMARY markers."""
    all_vulns = []
    for session in engagement_data.get("sessions", []):
        all_vulns.extend(session.get("vulnerabilities", []))
    vuln_summary = "\n".join(
        f"- {v['vuln_name']} ({v['severity']})" for v in all_vulns[:20]
    )
    prompt_text = (
        f"{EXECUTIVE_SUMMARY_PROMPT}\n\n"
        f"ENGAGEMENT: {engagement_data.get('engagement', {}).get('engagement_name', 'Unknown')}\n"
        f"CLIENT: {engagement_data.get('engagement', {}).get('client_name', 'Unknown')}\n"
        f"TOTAL VULNERABILITIES: {len(all_vulns)}\n"
        f"FINDINGS:\n{vuln_summary}"
    )
    response = ask_ollama(prompt_text)
    match = re.search(r'EXEC_SUMMARY_START\s*(.*?)\s*EXEC_SUMMARY_END', response, re.DOTALL)
    return match.group(1).strip() if match else response[:1000]


def compare_retest(original_data, retest_data):
    """Compare two sessions. Returns comparison dict."""
    orig_vulns = original_data.get("vulnerabilities", [])
    retest_vulns = retest_data.get("vulnerabilities", [])
    prompt_text = (
        f"{RETEST_COMPARISON_PROMPT}\n\n"
        f"ORIGINAL FINDINGS:\n" +
        "\n".join(f"VULN: {v['vuln_name']} | SEVERITY: {v['severity']}" for v in orig_vulns) +
        f"\n\nRETEST FINDINGS:\n" +
        "\n".join(f"VULN: {v['vuln_name']} | SEVERITY: {v['severity']}" for v in retest_vulns)
    )
    response = ask_ollama(prompt_text)
    comparisons = []
    for match in re.finditer(
        r'RETEST_FINDING:\s*(.+?)\s*\|\s*ORIGINAL_SEVERITY:\s*(.+?)\s*\|\s*STATUS:\s*(\w+)',
        response
    ):
        comparisons.append({
            "vuln_name": match.group(1).strip(),
            "original_severity": match.group(2).strip(),
            "status": match.group(3).strip(),
        })
    score_match = re.search(r'REMEDIATION_SCORE:\s*(\d+)', response)
    summary_match = re.search(r'RETEST_SUMMARY:\s*(.+)', response)
    return {
        "findings_comparison": comparisons,
        "new_findings": parse_vulnerabilities(response),
        "remediation_score": int(score_match.group(1)) if score_match else 0,
        "retest_summary": summary_match.group(1).strip() if summary_match else "",
    }


# ─────────────────────────────────────────────
# CLOUD AND SEGMENTATION PARSERS
# ─────────────────────────────────────────────

def parse_cloud_findings(response):
    """Parse CLOUD_FINDING: blocks from LLM response."""
    findings = []
    pattern = re.compile(
        r'CLOUD_FINDING:\s*(.+?)\s*\|\s*PROVIDER:\s*(\w+)\s*\|\s*SERVICE:\s*(\w+)\s*\n'
        r'SEVERITY:\s*(\w+)\s*\|\s*RESOURCE:\s*(.+?)\s*\n'
        r'DESCRIPTION:\s*(.+?)\s*\n'
        r'RECOMMENDATION:\s*(.+?)(?=\n\n|\nCLOUD_|\Z)',
        re.DOTALL
    )
    for m in pattern.finditer(response):
        findings.append({
            "finding_title": m.group(1).strip(),
            "provider": m.group(2).strip().lower(),
            "service": m.group(3).strip().lower(),
            "severity": m.group(4).strip().lower(),
            "resource_id": m.group(5).strip(),
            "description": m.group(6).strip(),
            "recommendation": m.group(7).strip(),
        })
    return findings


def parse_cloud_risk(response):
    """Extract CLOUD_RISK level from LLM response."""
    m = re.search(r'CLOUD_RISK:\s*(\w+)', response)
    return m.group(1).lower() if m else "medium"


def parse_cloud_summary(response):
    """Extract CLOUD_SUMMARY from LLM response."""
    m = re.search(r'CLOUD_SUMMARY:\s*(.+?)(?=\n[A-Z]|\Z)', response, re.DOTALL)
    return m.group(1).strip() if m else ""


def parse_seg_results(response):
    """Parse SEG_RESULT: lines from LLM response."""
    results = []
    for m in re.finditer(
        r'SEG_RESULT:\s*(.+?)\s*→\s*(.+?):(\d+)\s*\|\s*STATUS:\s*(\w+)\s*\|\s*EXPECTED:\s*(\w+)',
        response
    ):
        results.append({
            "source": m.group(1).strip(),
            "dest_host": m.group(2).strip(),
            "dest_port": int(m.group(3)),
            "result": m.group(4).strip().upper(),
            "expected": m.group(5).strip().lower(),
        })
    return results


def parse_seg_compliant(response):
    """Extract SEG_COMPLIANT from LLM response."""
    m = re.search(r'SEG_COMPLIANT:\s*(\w+)', response)
    return m.group(1).upper() if m else "PARTIAL"


def parse_seg_narrative(response):
    """Extract SEG_NARRATIVE from LLM response."""
    m = re.search(r'SEG_NARRATIVE:\s*(.+?)(?=\nPCI_|\Z)', response, re.DOTALL)
    return m.group(1).strip() if m else ""


def parse_empire_findings(response):
    """Parse EMPIRE_FINDING: blocks from LLM response."""
    findings = []
    for m in re.finditer(
        r'EMPIRE_FINDING:\s*(.+?)\s*\|\s*TYPE:\s*(\w+)\s*\nRISK:\s*(\w+)',
        response
    ):
        findings.append({
            "finding": m.group(1).strip(),
            "finding_type": m.group(2).strip(),
            "risk": m.group(3).strip().lower(),
        })
    return findings


def analyse_cloud(provider, cloud_data_str, engagement_id=None):
    """
    Run cloud-specific LLM analysis.
    provider: 'aws' | 'azure' | 'gcp'
    Returns dict with findings, risk, summary, full_response.
    """
    system_prompt = CLOUD_PHASE_PROMPTS.get(provider, CLOUD_AWS_PROMPT)
    context_str = build_engagement_context_string(engagement_id) if engagement_id else ""
    full_prompt = f"{system_prompt}\n\n{context_str}CLOUD DATA:\n{cloud_data_str}"
    response = ask_ollama(full_prompt)
    return {
        "full_response": response,
        "findings": parse_cloud_findings(response),
        "risk_level": parse_cloud_risk(response),
        "summary": parse_cloud_summary(response),
        "provider": provider,
    }


def analyse_segmentation(seg_test_results_str, engagement_id=None):
    """
    Run segmentation analysis via LLM.
    seg_test_results_str: formatted test results string.
    Returns dict with compliance status, narrative, findings.
    """
    context_str = build_engagement_context_string(engagement_id) if engagement_id else ""
    full_prompt = (f"{SEGMENTATION_ANALYSIS_PROMPT}\n\n{context_str}"
                   f"SEGMENTATION TEST RESULTS:\n{seg_test_results_str}")
    response = ask_ollama(full_prompt)
    return {
        "full_response": response,
        "seg_results": parse_seg_results(response),
        "compliant": parse_seg_compliant(response),
        "narrative": parse_seg_narrative(response),
    }
