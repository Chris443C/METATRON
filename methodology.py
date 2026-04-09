#!/usr/bin/env python3
"""METATRON - methodology.py  10-phase professional pentest orchestrator."""
import db
import llm
import tools
import enum_tools
import engagement as eng


PHASES = {
    1:  "Pre-Engagement",
    2:  "Reconnaissance",
    3:  "Enumeration",
    4:  "Vulnerability Analysis",
    5:  "Exploitation",
    6:  "Post-Exploitation",
    7:  "Reporting",
    8:  "Retest",
    9:  "Cloud Assessment",
    10: "Segmentation Testing",
}


def display_phase_progress(completed_phases):
    from metatron import divider
    divider()
    for num, name in PHASES.items():
        status = "[✓]" if num in completed_phases else "[ ]"
        print(f"  {status} Phase {num:>2} — {name}")
    divider()


def run_methodology_workflow(engagement_id):
    """Top-level 10-phase workflow loop."""
    from metatron import prompt, success, warn, info, error, divider, confirm
    completed = set()
    e = db.get_engagement(engagement_id)
    db.update_engagement_status(engagement_id, "active")
    session_state = {
        "sl_no": None, "raw_scan": "", "enum_data": "",
        "attack_paths": [], "exploit_results": []
    }
    while True:
        display_phase_progress(completed)
        info(f"Engagement: {e['engagement_name']} | Client: {e['client_name']}")
        print()
        for num, name in PHASES.items():
            print(f"  [{num:>2}] Phase {num} — {name}")
        print("   [b] Back to main menu (progress saved)")
        choice = input("\n  Select phase: ").strip().lower()
        if choice in ("b", "s", "back"):
            db.update_engagement_status(
                engagement_id, "reporting" if 6 in completed else "active"
            )
            success("Engagement progress saved.")
            break
        try:
            phase_num = int(choice)
        except ValueError:
            continue
        if phase_num == 1:
            eng.view_engagement_summary(engagement_id)
            if confirm("Edit scope?"):
                eng.define_scope_interactive(engagement_id)
            completed.add(1)
        elif phase_num == 2:
            sl_no, raw = phase_2_recon(engagement_id)
            if sl_no:
                session_state["sl_no"] = sl_no
                session_state["raw_scan"] = raw
                completed.add(2)
        elif phase_num == 3:
            if not session_state["sl_no"]:
                warn("Run Phase 2 first to create a session.")
                continue
            enum_str = phase_3_enumeration(
                engagement_id, session_state["sl_no"], session_state["raw_scan"]
            )
            session_state["enum_data"] = enum_str
            completed.add(3)
        elif phase_num == 4:
            if not session_state["sl_no"]:
                warn("Run Phase 2 first.")
                continue
            combined = session_state["raw_scan"] + "\n\n" + session_state["enum_data"]
            paths = phase_4_vuln_analysis(
                engagement_id, session_state["sl_no"], combined
            )
            session_state["attack_paths"] = paths
            completed.add(4)
        elif phase_num == 5:
            if not session_state["sl_no"]:
                warn("Run Phase 2 first.")
                continue
            results = phase_5_exploitation(
                engagement_id, session_state["sl_no"], session_state["attack_paths"]
            )
            session_state["exploit_results"] = results
            completed.add(5)
        elif phase_num == 6:
            if not session_state["sl_no"]:
                warn("Run Phase 2 first.")
                continue
            import post_exploit
            post_exploit.post_exploit_menu(
                engagement_id, session_state["sl_no"], session_state["exploit_results"]
            )
            completed.add(6)
        elif phase_num == 7:
            if not session_state["sl_no"]:
                warn("Run Phase 2 first.")
                continue
            phase_7_reporting(engagement_id, session_state["sl_no"])
            completed.add(7)
        elif phase_num == 8:
            phase_8_retest(engagement_id, session_state["sl_no"])
            completed.add(8)
        elif phase_num == 9:
            if not session_state["sl_no"]:
                warn("Run Phase 2 first to create a session.")
                continue
            phase_9_cloud_assessment(engagement_id, session_state["sl_no"])
            completed.add(9)
        elif phase_num == 10:
            if not session_state["sl_no"]:
                warn("Run Phase 2 first to create a session.")
                continue
            phase_10_segmentation(engagement_id, session_state["sl_no"])
            completed.add(10)


def _get_target_for_sl(sl_no):
    """Get target string for a given sl_no."""
    history = db.get_all_history()
    return next((h[1] for h in history if h[0] == sl_no), "unknown")


def phase_2_recon(engagement_id):
    """Reconnaissance phase. Returns (sl_no, raw_scan)."""
    from metatron import prompt, success, warn, info, error, divider, confirm
    from tools import interactive_tool_run
    divider()
    info("PHASE 2 — RECONNAISSANCE")
    target = prompt("Enter target IP or domain: ")
    in_scope, reason = eng.check_target_in_scope(target, engagement_id)
    if not in_scope:
        error(f"OUT OF SCOPE: {reason}")
        if not confirm("Proceed anyway?"):
            return None, ""
    elif "caution" in reason:
        warn(f"Scope warning: {reason}")
    raw_scan = interactive_tool_run(target)
    sl_no = db.create_session(target)
    db.link_session_to_engagement(sl_no, engagement_id, "recon")
    db.save_evidence(sl_no, engagement_id, "recon", "command_output",
                     f"Recon: {target}", raw_scan)
    info("Running AI analysis (Phase 2 — Recon)...")
    result = llm.analyse_phase(target, raw_scan, 2, engagement_id)
    for v in result.get("vulnerabilities", []):
        vid = db.save_vulnerability(sl_no, v["vuln_name"], v["severity"],
                                    v["port"], v["service"], v.get("description", ""))
        if v.get("fix"):
            db.save_fix(sl_no, vid, v["fix"])
    for ex in result.get("exploits", []):
        db.save_exploit(sl_no, ex.get("exploit_name", ""), ex.get("tool_used", ""),
                        ex.get("payload", ""), ex.get("result", ""), ex.get("notes", ""))
    db.save_summary(sl_no, raw_scan, result["full_response"],
                    result.get("risk_level", "MEDIUM"))
    success(f"Phase 2 complete. Session SL#{sl_no}")
    return sl_no, raw_scan


def phase_3_enumeration(engagement_id, sl_no, raw_scan):
    """Enumeration phase. Returns combined enum string."""
    from metatron import success, warn, info, divider
    divider()
    info("PHASE 3 — ENUMERATION")
    target = _get_target_for_sl(sl_no)
    info(f"Target: {target}")
    print()
    print("  Select enumeration types to run:")
    print("  [1] Web directory brute force (gobuster)")
    print("  [2] SMB enumeration (enum4linux)")
    print("  [3] LDAP enumeration (nmap)")
    print("  [4] API endpoint discovery")
    print("  [a] All")
    print("  [b] Back to phase menu")
    choice = input("  Choice(s) e.g. '1 3' or 'a': ").strip().lower()
    if choice == "b":
        return ""
    options = {
        "web_dirs":      "a" in choice or "1" in choice,
        "smb":           "a" in choice or "2" in choice,
        "ldap":          "a" in choice or "3" in choice,
        "api_discovery": "a" in choice or "4" in choice,
    }

    combined_sections = []

    if options["web_dirs"]:
        info("Running: gobuster web directory brute force...")
        result = enum_tools.run_web_dir_enum(target)
        output = result.get("raw_output", "(no output)")
        print(output[:2000])
        if len(output) > 2000:
            print(f"  ... [{len(output) - 2000} chars truncated]")
        combined_sections.append(f"--- WEB DIRS ---\n{output}")
        if "not found" in output.lower() or "error" in output.lower():
            warn("gobuster may not be installed: sudo apt install gobuster")

    if options["smb"]:
        info("Running: enum4linux SMB enumeration...")
        result = enum_tools.run_enum4linux(target)
        output = result.get("raw_output", "(no output)")
        print(output[:2000])
        combined_sections.append(f"--- SMB ---\n{output}")
        if "not found" in output.lower() or "command not found" in output.lower():
            warn("enum4linux may not be installed — see README for install steps")

    if options["ldap"]:
        info("Running: nmap LDAP enumeration...")
        result = enum_tools.run_ldap_enum(target)
        output = result.get("raw_output", "(no output)")
        print(output[:2000])
        combined_sections.append(f"--- LDAP ---\n{output}")

    if options["api_discovery"]:
        info("Running: API endpoint discovery...")
        result = enum_tools.run_api_discovery(target)
        output = result.get("raw_output", "(no output)")
        print(output[:2000])
        combined_sections.append(f"--- API ENDPOINTS ---\n{output}")

    if not combined_sections:
        warn("No enumeration types selected.")
        return ""

    enum_str = f"=== ENUMERATION: {target} ===\n" + "\n\n".join(combined_sections)
    db.save_evidence(sl_no, engagement_id, "enumeration", "command_output",
                     f"Enumeration: {target}", enum_str)
    info("Running AI analysis (Phase 3 — Enumeration)...")
    llm.analyse_phase(target, raw_scan + "\n\n" + enum_str, 3, engagement_id)
    success("Phase 3 complete.")
    return enum_str


def phase_4_vuln_analysis(engagement_id, sl_no, combined_scan_data):
    """Vulnerability analysis phase. Returns list of attack path dicts."""
    from metatron import success, info, divider
    divider()
    info("PHASE 4 — VULNERABILITY ANALYSIS")
    target = _get_target_for_sl(sl_no)
    result = llm.analyse_phase(target, combined_scan_data, 4, engagement_id)
    attack_paths = result.get("attack_paths", [])
    for ap in attack_paths:
        db.save_attack_path(sl_no, engagement_id, ap["path_name"], ap["steps"],
                            ap["severity"], None, ap.get("narrative", ""))
    if attack_paths:
        success(f"Phase 4 complete. {len(attack_paths)} attack path(s) identified.")
        for i, ap in enumerate(attack_paths, 1):
            print(f"  [{i}] {ap['path_name']} ({ap['severity'].upper()})")
            print(f"       {ap.get('narrative', '')[:100]}")
    else:
        info("Phase 4 complete. No multi-step attack paths identified.")
    return attack_paths


def phase_5_exploitation(engagement_id, sl_no, attack_paths):
    """Exploitation phase. Human executes; METATRON records. Returns exploit result dicts."""
    from metatron import prompt, success, warn, info, divider, confirm
    divider()
    info("PHASE 5 — EXPLOITATION (Human-Led)")
    target = _get_target_for_sl(sl_no)
    if not attack_paths:
        info("No attack paths from Phase 4.")
    context = "\n".join(
        f"ATTACK_PATH: {ap['path_name']}\n" +
        "\n".join(f"STEP_{i+1}: {s}" for i, s in enumerate(ap["steps"]))
        for ap in attack_paths
    ) if attack_paths else "Vulnerabilities from recon phase"
    info("Generating exploitation guidance...")
    result = llm.analyse_phase(target, context, 5, engagement_id)
    print("\n  AI Exploitation Suggestions:")
    print(result["full_response"][:2000])
    results = []
    while confirm("Record an exploitation attempt?"):
        exploit_name = prompt("Exploit/attack name: ")
        tool_used    = prompt("Tool used: ")
        payload      = prompt("Command/payload used: ")
        res          = prompt("Result (success/partial/failed): ")
        notes        = prompt("Notes / evidence: ")
        evidence_text = prompt("Paste command output as evidence (or press Enter to skip): ").strip()
        if evidence_text:
            db.save_evidence(sl_no, engagement_id, "exploitation", "command_output",
                             f"Exploit: {exploit_name}", evidence_text)
        db.save_exploit(sl_no, exploit_name, tool_used, payload, res, notes)
        results.append({"exploit_name": exploit_name, "result": res, "success": res == "success"})
        success("Exploitation attempt recorded.")
    return results


def phase_7_reporting(engagement_id, sl_no):
    """Reporting phase. Generates executive summary and offers export."""
    from metatron import success, info, divider
    import export
    divider()
    info("PHASE 7 — REPORTING")
    info("Generating executive summary...")
    all_data = db.get_session(sl_no)
    eng_data = {
        "engagement": db.get_engagement(engagement_id),
        "sessions": [all_data],
    }
    exec_summary = llm.generate_executive_summary(eng_data)
    print("\n  EXECUTIVE SUMMARY:")
    print("  " + exec_summary.replace("\n", "\n  "))
    db.save_evidence(sl_no, engagement_id, "reporting", "note",
                     "Executive Summary", exec_summary)
    export.export_menu(all_data)
    db.update_engagement_status(engagement_id, "reporting")
    success("Phase 7 complete.")


def phase_8_retest(engagement_id, original_sl_no):
    """Retest phase. Runs new scan and compares findings."""
    from metatron import retest_flow
    retest_flow(engagement_id, original_sl_no)


def phase_9_cloud_assessment(engagement_id, sl_no):
    """Phase 9: Cloud assessment for AWS, Azure, and/or GCP."""
    import cloud_tools
    from metatron import success, warn, info, divider
    divider()
    info("PHASE 9 — CLOUD ASSESSMENT")
    print("  Select cloud provider(s) to assess:")
    print("  [1] AWS")
    print("  [2] Azure")
    print("  [3] GCP")
    print("  [a] All available")
    print("  [b] Back to phase menu")
    choice = input("  Choice(s) e.g. '1 2' or 'a': ").strip().lower()
    if choice == "b":
        return []
    providers_to_test = []
    if "a" in choice or "1" in choice:
        ok, msg = cloud_tools.validate_aws_credentials()
        if ok:
            providers_to_test.append("aws")
            success(f"AWS: {msg}")
        else:
            warn(f"AWS skipped: {msg}")
    if "a" in choice or "2" in choice:
        ok, msg = cloud_tools.validate_azure_credentials()
        if ok:
            providers_to_test.append("azure")
            success(f"Azure: {msg}")
        else:
            warn(f"Azure skipped: {msg}")
    if "a" in choice or "3" in choice:
        ok, msg = cloud_tools.validate_gcp_credentials()
        if ok:
            providers_to_test.append("gcp")
            success(f"GCP: {msg}")
        else:
            warn(f"GCP skipped: {msg}")
    if not providers_to_test:
        warn("No cloud credentials available. Configure credentials externally and retry.")
        return []
    all_cloud_findings = []
    for provider in providers_to_test:
        info(f"Running {provider.upper()} assessment...")
        if provider == "aws":
            raw_results = cloud_tools.run_aws_assessment(engagement_id)
        elif provider == "azure":
            raw_results = cloud_tools.run_azure_assessment()
        else:
            raw_results = cloud_tools.run_gcp_assessment()
        if "error" in raw_results:
            warn(f"{provider.upper()} assessment error: {raw_results['error']}")
            continue
        data_str = cloud_tools.format_cloud_results_for_llm(provider, raw_results)
        db.save_evidence(sl_no, engagement_id, "cloud_assessment", "command_output",
                         f"Cloud assessment: {provider.upper()}", data_str)
        info(f"Running AI analysis for {provider.upper()}...")
        result = llm.analyse_cloud(provider, data_str, engagement_id)
        for f in result.get("findings", []):
            db.save_cloud_finding(
                sl_no, engagement_id, provider,
                f.get("service", "unknown"), f.get("finding_title", ""),
                f.get("severity", "medium"), f.get("resource_id", ""),
                f.get("region", ""), f.get("description", ""),
                f.get("recommendation", ""), data_str[:5000], "cli+llm"
            )
            all_cloud_findings.append(f)
        success(f"{provider.upper()}: {len(result.get('findings', []))} findings | "
                f"Risk: {result.get('risk_level', 'unknown').upper()}")
    info(f"Phase 9 complete. Total cloud findings: {len(all_cloud_findings)}")
    return all_cloud_findings


def phase_10_segmentation(engagement_id, sl_no):
    """Phase 10: PCI DSS 11.4.5 segmentation testing via ncat."""
    import segmentation_tools
    from metatron import success, warn, info, divider
    divider()
    info("PHASE 10 — SEGMENTATION TESTING (PCI DSS 11.4.5)")
    info("Tests network isolation between segments. Evidence saved to DB for reporting.")
    divider()
    results, evidence_table = segmentation_tools.interactive_segmentation_wizard(engagement_id)
    if not results:
        return []
    db.save_evidence(sl_no, engagement_id, "segmentation", "command_output",
                     "PCI 11.4.5 Segmentation Test Evidence", evidence_table)
    for r in results:
        db.save_segmentation_test(
            sl_no, engagement_id,
            r["source_host"], r["dest_host"], r["dest_port"],
            r["protocol"], r["expected"], r["result"],
            r["tool_used"], r["raw_output"], r["tester_name"]
        )
    info("Running AI analysis of segmentation results...")
    seg_analysis = llm.analyse_segmentation(evidence_table, engagement_id)
    db.save_evidence(sl_no, engagement_id, "segmentation", "note",
                     "AI Segmentation Analysis", seg_analysis.get("narrative", ""))
    compliant = seg_analysis.get("compliant", "PARTIAL")
    narrative = seg_analysis.get("narrative", "")
    fail_count = sum(1 for r in results if r["result"] == "FAIL")
    if fail_count > 0:
        warn(f"PCI COMPLIANCE: {compliant} — {fail_count} segmentation failure(s) require remediation")
    else:
        success(f"PCI COMPLIANCE: {compliant} — All segmentation controls verified")
    if narrative:
        print(f"\n  AI Assessment: {narrative[:300]}")
    success(f"Phase 10 complete. {len(results)} tests run.")
    return results
