#!/usr/bin/env python3
"""
METATRON - metatron.py
Main CLI entry point. Wires db.py + tools.py + search.py + llm.py together.
Run with: python metatron.py
"""
from export import export_menu
import os
import sys
from db import (
    get_connection,
    create_session,
    save_vulnerability,
    save_fix,
    save_exploit,
    save_summary,
    get_all_history,
    get_session,
    get_vulnerabilities,
    get_fixes,
    get_exploits,
    edit_vulnerability,
    edit_fix,
    edit_exploit,
    edit_summary_risk,
    delete_vulnerability,
    delete_exploit,
    delete_fix,
    delete_full_session,
    print_history,
    print_session
)
from tools import interactive_tool_run, format_recon_for_llm, run_default_recon
from llm import analyse_target


# ─────────────────────────────────────────────
# BANNER
# ─────────────────────────────────────────────

def banner():
    os.system("clear")
    print("""
\033[91m
    ███╗   ███╗███████╗████████╗ █████╗ ████████╗██████╗  ██████╗ ███╗   ██╗
    ████╗ ████║██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██╔══██╗██╔═══██╗████╗  ██║
    ██╔████╔██║█████╗     ██║   ███████║   ██║   ██████╔╝██║   ██║██╔██╗ ██║
    ██║╚██╔╝██║██╔══╝     ██║   ██╔══██║   ██║   ██╔══██╗██║   ██║██║╚██╗██║
    ██║ ╚═╝ ██║███████╗   ██║   ██║  ██║   ██║   ██║  ██║╚██████╔╝██║ ╚████║
    ╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
\033[0m
    \033[90mAI Penetration Testing Assistant  |  Model: metatron-qwen  |  Parrot OS\033[0m
    \033[90m─────────────────────────────────────────────────────────────────────\033[0m
""")


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def divider(label=""):
    if label:
        print(f"\n\033[33m{'─'*20} {label} {'─'*20}\033[0m")
    else:
        print(f"\033[90m{'─'*60}\033[0m")


def prompt(text):
    return input(f"\033[36m{text}\033[0m").strip()


def success(text):
    print(f"\033[92m[+] {text}\033[0m")


def warn(text):
    print(f"\033[93m[!] {text}\033[0m")


def error(text):
    print(f"\033[91m[✗] {text}\033[0m")


def info(text):
    print(f"\033[94m[*] {text}\033[0m")


def confirm(question: str) -> bool:
    ans = prompt(f"{question} [y/N]: ").lower()
    return ans == "y"


# ─────────────────────────────────────────────
# NEW SCAN
# ─────────────────────────────────────────────

def new_scan(return_sl_no=False):
    divider("NEW SCAN")
    target = prompt("[?] Enter target IP or domain: ")
    if not target:
        warn("No target entered.")
        return

    # check if target was scanned before
    history = get_all_history()
    past = [row for row in history if row[1] == target]
    if past:
        warn(f"Target '{target}' has been scanned before ({len(past)} time(s)).")
        if not confirm("Continue with a new scan?"):
            return

    # create session in history table first
    sl_no = create_session(target)
    success(f"Session created — SL# {sl_no}")

    # run recon tools
    divider("RECON")
    info("Choose recon tools to run:")
    raw_scan = interactive_tool_run(target)

    if not raw_scan.strip():
        warn("No scan data collected. Aborting.")
        delete_full_session(sl_no)
        return

    # send to AI
    divider("AI ANALYSIS")
    result = analyse_target(target, raw_scan)

    # ── save everything to DB ──────────────────
    divider("SAVING TO DATABASE")

    # save vulnerabilities and their fixes
    for vuln in result["vulnerabilities"]:
        vuln_id = save_vulnerability(
            sl_no,
            vuln["vuln_name"],
            vuln["severity"],
            vuln["port"],
            vuln["service"],
            vuln["description"]
        )
        if vuln.get("fix"):
            save_fix(sl_no, vuln_id, vuln["fix"], source="ai")
        success(f"Saved vuln: {vuln['vuln_name']} [{vuln['severity']}]")

    # save exploits
    for exp in result["exploits"]:
        save_exploit(
            sl_no,
            exp["exploit_name"],
            exp["tool_used"],
            exp["payload"],
            exp["result"],
            exp["notes"]
        )
        success(f"Saved exploit: {exp['exploit_name']}")

    # save summary
    save_summary(
        sl_no,
        result["raw_scan"],
        result["full_response"],
        result["risk_level"]
    )

    success(f"All data saved. SL# {sl_no} | Risk: {result['risk_level']}")
    divider()

    # show results and offer edit/delete
    data = get_session(sl_no)
    print_session(data)

    if confirm("Edit or delete anything in this session?"):
        edit_delete_menu(sl_no)

    if return_sl_no:
        return sl_no


# ─────────────────────────────────────────────
# VIEW HISTORY
# ─────────────────────────────────────────────

def view_history():
    divider("SCAN HISTORY")
    rows = get_all_history()

    if not rows:
        warn("No scans in database yet.")
        return

    print_history(rows)

    sl_no_str = prompt("Enter SL# to view details (or press Enter to go back): ")
    if not sl_no_str:
        return

    try:
        sl_no = int(sl_no_str)
    except ValueError:
        error("Invalid SL#.")
        return

    data = get_session(sl_no)
    if not data["history"]:
        error(f"SL# {sl_no} not found.")
        return

    print_session(data)

    if confirm("Export this session?"):
        export_menu(data)

    if confirm("Edit or delete anything in this session?"):
        edit_delete_menu(sl_no)


# ─────────────────────────────────────────────
# EDIT / DELETE MENU
# ─────────────────────────────────────────────

def edit_delete_menu(sl_no: int):
    while True:
        divider(f"EDIT / DELETE — SL# {sl_no}")
        print("  [1] Edit a vulnerability")
        print("  [2] Edit a fix")
        print("  [3] Edit an exploit")
        print("  [4] Edit risk level")
        print("  [5] Delete a vulnerability")
        print("  [6] Delete a fix")
        print("  [7] Delete an exploit")
        print("  [8] Delete FULL session (all tables)")
        print("  [9] Back")
        divider()

        choice = prompt("Choice: ")

        # ── EDIT VULNERABILITY ─────────────────
        if choice == "1":
            vulns = get_vulnerabilities(sl_no)
            if not vulns:
                warn("No vulnerabilities recorded for this session.")
                continue

            print("\n[ VULNERABILITIES ]")
            for v in vulns:
                print(f"  id={v[0]} | {v[2]} | {v[3]} | port {v[4]} | {v[5]}")

            vid = prompt("Enter vulnerability id to edit: ")
            if not vid.isdigit():
                error("Invalid id.")
                continue

            print("  Fields: vuln_name / severity / port / service / description")
            field = prompt("Field to edit: ").strip()
            value = prompt(f"New value for '{field}': ")
            edit_vulnerability(int(vid), field, value)

        # ── EDIT FIX ──────────────────────────
        elif choice == "2":
            fixes = get_fixes(sl_no)
            if not fixes:
                warn("No fixes recorded for this session.")
                continue

            print("\n[ FIXES ]")
            for f in fixes:
                print(f"  id={f[0]} | vuln_id={f[2]} | {f[3][:80]}")

            fid = prompt("Enter fix id to edit: ")
            if not fid.isdigit():
                error("Invalid id.")
                continue

            new_text = prompt("New fix text: ")
            edit_fix(int(fid), new_text)

        # ── EDIT EXPLOIT ──────────────────────
        elif choice == "3":
            exploits = get_exploits(sl_no)
            if not exploits:
                warn("No exploits recorded for this session.")
                continue

            print("\n[ EXPLOITS ]")
            for e in exploits:
                print(f"  id={e[0]} | {e[2]} | tool: {e[3]} | result: {e[5]}")

            eid = prompt("Enter exploit id to edit: ")
            if not eid.isdigit():
                error("Invalid id.")
                continue

            print("  Fields: exploit_name / tool_used / payload / result / notes")
            field = prompt("Field to edit: ").strip()
            value = prompt(f"New value for '{field}': ")
            edit_exploit(int(eid), field, value)

        # ── EDIT RISK LEVEL ───────────────────
        elif choice == "4":
            print("  Options: CRITICAL / HIGH / MEDIUM / LOW")
            risk = prompt("New risk level: ").upper()
            if risk not in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
                error("Invalid risk level.")
                continue
            edit_summary_risk(sl_no, risk)

        # ── DELETE VULNERABILITY ──────────────
        elif choice == "5":
            vulns = get_vulnerabilities(sl_no)
            if not vulns:
                warn("No vulnerabilities to delete.")
                continue

            print("\n[ VULNERABILITIES ]")
            for v in vulns:
                print(f"  id={v[0]} | {v[2]} | {v[3]}")

            vid = prompt("Enter vulnerability id to delete: ")
            if not vid.isdigit():
                error("Invalid id.")
                continue

            if confirm(f"Delete vulnerability id={vid} and its linked fixes?"):
                delete_vulnerability(int(vid))

        # ── DELETE FIX ────────────────────────
        elif choice == "6":
            fixes = get_fixes(sl_no)
            if not fixes:
                warn("No fixes to delete.")
                continue

            print("\n[ FIXES ]")
            for f in fixes:
                print(f"  id={f[0]} | vuln_id={f[2]} | {f[3][:80]}")

            fid = prompt("Enter fix id to delete: ")
            if not fid.isdigit():
                error("Invalid id.")
                continue

            if confirm(f"Delete fix id={fid}?"):
                delete_fix(int(fid))

        # ── DELETE EXPLOIT ────────────────────
        elif choice == "7":
            exploits = get_exploits(sl_no)
            if not exploits:
                warn("No exploits to delete.")
                continue

            print("\n[ EXPLOITS ]")
            for e in exploits:
                print(f"  id={e[0]} | {e[2]} | result: {e[5]}")

            eid = prompt("Enter exploit id to delete: ")
            if not eid.isdigit():
                error("Invalid id.")
                continue

            if confirm(f"Delete exploit id={eid}?"):
                delete_exploit(int(eid))

        # ── DELETE FULL SESSION ───────────────
        elif choice == "8":
            if confirm(f"\n\033[91mPermanently delete ENTIRE session SL# {sl_no} from all tables?\033[0m"):
                delete_full_session(sl_no)
                success(f"Session SL# {sl_no} wiped.")
                return   # go back to main menu

        # ── BACK ──────────────────────────────
        elif choice == "9":
            break

        else:
            warn("Invalid choice.")


# ─────────────────────────────────────────────
# DB CONNECTION CHECK
# ─────────────────────────────────────────────

def check_db():
    try:
        conn = get_connection()
        conn.close()
        return True
    except Exception as e:
        error(f"MariaDB connection failed: {e}")
        error("Make sure MariaDB is running: sudo systemctl start mariadb")
        return False


# ─────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────

def retest_flow(engagement_id=None, original_sl_no=None):
    """Phase 8 retest workflow — runs new scan and compares with original."""
    divider()
    info("RETEST WORKFLOW")
    if not original_sl_no:
        view_history()
        try:
            original_sl_no = int(prompt("Enter original scan SL# to retest: "))
        except ValueError:
            warn("Invalid SL#.")
            return
    original_data = get_session(original_sl_no)
    if not original_data:
        error(f"SL#{original_sl_no} not found.")
        return
    info(f"Original scan: {original_data['history'][1]} on {original_data['history'][2]}")
    info(f"Vulnerabilities: {len(original_data.get('vulnerabilities', []))}")
    if confirm("Run a new scan now for retest?"):
        new_sl_no = new_scan(return_sl_no=True)
    else:
        try:
            new_sl_no = int(prompt("Enter existing scan SL# to use as retest: "))
        except ValueError:
            warn("Invalid SL#.")
            return
    if not new_sl_no:
        return
    retest_data = get_session(new_sl_no)
    info("Comparing findings with AI...")
    from llm import compare_retest
    comparison = compare_retest(original_data, retest_data)
    divider()
    info("RETEST RESULTS")
    print(f"  Remediation score: {comparison['remediation_score']}%")
    for fc in comparison["findings_comparison"]:
        status_sym = "✓" if fc["status"] == "FIXED" else "✗"
        print(f"  [{status_sym}] {fc['vuln_name']} — {fc['status']}")
    if comparison["new_findings"]:
        warn(f"  {len(comparison['new_findings'])} NEW finding(s) discovered!")
    print(f"\n  {comparison['retest_summary']}")
    overall = ("all_fixed" if comparison["remediation_score"] >= 100
               else "partial" if comparison["remediation_score"] > 0 else "none_fixed")
    from db import create_retest_session
    create_retest_session(original_sl_no, new_sl_no, engagement_id,
                          overall, comparison["retest_summary"])
    success("Retest session recorded.")


def engagement_menu():
    """Engagement management sub-menu."""
    import engagement as eng
    while True:
        divider()
        print("  [1] New engagement")
        print("  [2] Resume engagement")
        print("  [3] List all engagements")
        print("  [4] Back")
        choice = input("\n  Choice: ").strip()
        if choice == "1":
            import methodology
            eid = eng.new_engagement_wizard()
            if eid and confirm("Start methodology workflow now?"):
                methodology.run_methodology_workflow(eid)
        elif choice == "2":
            import methodology
            eid = eng.select_or_create_engagement()
            if eid:
                methodology.run_methodology_workflow(eid)
        elif choice == "3":
            eng.list_engagements()
        elif choice == "4":
            break


def _standalone_cloud_assessment():
    """Standalone cloud assessment outside of a full engagement."""
    divider()
    info("STANDALONE CLOUD ASSESSMENT")
    info("No engagement required — results saved to most recent scan session.")
    divider()
    sessions = get_all_history()
    if not sessions:
        warn("No scan sessions found. Run a Quick Scan first to create a session.")
        return
    sl_no = sessions[0][0]
    info(f"Using most recent session: SL#{sl_no}")
    import methodology
    methodology.phase_9_cloud_assessment(None, sl_no)


def _standalone_segmentation_test():
    """Standalone segmentation test outside of a full engagement."""
    divider()
    info("STANDALONE SEGMENTATION TESTING — PCI DSS 11.4.5")
    sessions = get_all_history()
    if not sessions:
        warn("No scan sessions found. Run a Quick Scan first to create a session.")
        return
    sl_no = sessions[0][0]
    info(f"Using most recent session: SL#{sl_no}")
    import methodology
    methodology.phase_10_segmentation(None, sl_no)


def main_menu():
    while True:
        banner()
        print("  \033[92m[1]\033[0m  New Engagement  (10-phase methodology)")
        print("  \033[92m[2]\033[0m  Quick Scan      (legacy, no engagement)")
        print("  \033[92m[3]\033[0m  View History")
        print("  \033[92m[4]\033[0m  Engagements")
        print("  \033[92m[5]\033[0m  Retest")
        print("  \033[92m[6]\033[0m  Cloud Assessment")
        print("  \033[92m[7]\033[0m  Segmentation Testing  (PCI 11.4.5)")
        print("  \033[92m[8]\033[0m  Export Report")
        print("  \033[92m[9]\033[0m  Exit")
        divider()

        choice = prompt("metatron> ")

        if choice == "1":
            import methodology
            import engagement as eng
            eid = eng.select_or_create_engagement()
            if eid:
                methodology.run_methodology_workflow(eid)
            input("\n\033[90mPress Enter to continue...\033[0m")

        elif choice == "2":
            new_scan()
            input("\n\033[90mPress Enter to continue...\033[0m")

        elif choice == "3":
            view_history()
            input("\n\033[90mPress Enter to continue...\033[0m")

        elif choice == "4":
            engagement_menu()
            input("\n\033[90mPress Enter to continue...\033[0m")

        elif choice == "5":
            retest_flow()
            input("\n\033[90mPress Enter to continue...\033[0m")

        elif choice == "6":
            _standalone_cloud_assessment()
            input("\n\033[90mPress Enter to continue...\033[0m")

        elif choice == "7":
            _standalone_segmentation_test()
            input("\n\033[90mPress Enter to continue...\033[0m")

        elif choice == "8":
            view_history()
            input("\n\033[90mPress Enter to continue...\033[0m")

        elif choice == "9":
            print("\n\033[91m[*] Shutting down Metatron. Stay legal.\033[0m\n")
            sys.exit(0)

        else:
            warn("Invalid choice.")


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    if not check_db():
        sys.exit(1)
    main_menu()
