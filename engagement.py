#!/usr/bin/env python3
"""METATRON - engagement.py  Pre-engagement scope management. Phase 1."""
import db


def new_engagement_wizard():
    """Interactive wizard to create a new engagement. Returns engagement_id."""
    from metatron import prompt, success, warn, info, divider, confirm
    divider()
    info("NEW ENGAGEMENT SETUP — Phase 1: Pre-Engagement")
    divider()
    client_name = prompt("Client name: ")
    engagement_name = prompt("Engagement name (e.g. External Pentest Q2 2025): ")
    print("\n  Test type:")
    print("  [1] Black box (no prior knowledge)")
    print("  [2] Grey box (partial knowledge)")
    print("  [3] White box (full knowledge)")
    tt_map = {"1": "black", "2": "grey", "3": "white"}
    tt = tt_map.get(input("  Choice [1/2/3]: ").strip(), "black")
    start_date = prompt("Start date (YYYY-MM-DD) [optional]: ").strip() or None
    end_date = prompt("End date (YYYY-MM-DD) [optional]: ").strip() or None
    testing_window = prompt("Testing window (e.g. Mon-Fri 09:00-17:00 UTC) [optional]: ").strip()
    notes = prompt("Notes / special instructions [optional]: ").strip()
    eid = db.create_engagement(client_name, engagement_name, tt,
                               start_date, end_date, testing_window, notes)
    success(f"Engagement #{eid} created: {engagement_name}")
    define_scope_interactive(eid)
    return eid


def define_scope_interactive(engagement_id):
    """Loop prompting in-scope and out-of-scope targets until user types 'done'."""
    from metatron import success, warn, info, divider
    divider()
    info("SCOPE DEFINITION — enter targets (type 'done' to finish)")
    info("Format: 192.168.1.0/24  or  example.com  or  http://app.example.com")
    divider()
    while True:
        target = input("  In-scope target (or 'done'): ").strip()
        if target.lower() == "done":
            break
        if target:
            desc = input("  Description [optional]: ").strip()
            db.add_scope_item(engagement_id, "in_scope", target, desc)
            success(f"Added in-scope: {target}")
    while True:
        target = input("  Out-of-scope target (or 'done'): ").strip()
        if target.lower() == "done":
            break
        if target:
            desc = input("  Description [optional]: ").strip()
            db.add_scope_item(engagement_id, "out_of_scope", target, desc)
            warn(f"Marked out-of-scope: {target}")


def view_engagement_summary(engagement_id):
    """Print formatted engagement details and scope."""
    from metatron import warn, info, divider
    e = db.get_engagement(engagement_id)
    if not e:
        warn(f"Engagement #{engagement_id} not found.")
        return
    scope = db.get_scope_items(engagement_id)
    divider()
    info(f"ENGAGEMENT #{e['id']}: {e['engagement_name']}")
    print(f"  Client:   {e['client_name']}")
    print(f"  Type:     {e['test_type']} box")
    print(f"  Dates:    {e['start_date']} → {e['end_date']}")
    print(f"  Window:   {e['testing_window'] or 'Not specified'}")
    print(f"  Status:   {e['status']}")
    if e["notes"]:
        print(f"  Notes:    {e['notes']}")
    print()
    print("  IN SCOPE:")
    for s in scope["in_scope"]:
        print(f"    + {s['target']}  {s['description'] or ''}")
    if not scope["in_scope"]:
        warn("  No in-scope items defined.")
    print()
    print("  OUT OF SCOPE:")
    for s in scope["out_of_scope"]:
        print(f"    - {s['target']}  {s['description'] or ''}")
    divider()


def list_engagements():
    """Print table of all engagements."""
    from metatron import info, divider
    rows = db.get_all_engagements()
    if not rows:
        info("No engagements found.")
        return
    divider()
    print(f"  {'ID':<5} {'CLIENT':<20} {'ENGAGEMENT':<35} {'TYPE':<8} {'STATUS':<12}")
    divider()
    for e in rows:
        print(f"  {e['id']:<5} {e['client_name'][:18]:<20} "
              f"{e['engagement_name'][:33]:<35} {e['test_type']:<8} {e['status']:<12}")
    divider()


def select_or_create_engagement():
    """Show menu to start new or resume existing engagement. Returns engagement_id."""
    from metatron import prompt, success, warn
    existing = db.get_all_engagements()
    print("\n  [1] Start a new engagement")
    if existing:
        print("  [2] Resume an existing engagement")
    choice = input("\n  Choice: ").strip()
    if choice == "1":
        return new_engagement_wizard()
    elif choice == "2" and existing:
        list_engagements()
        try:
            eid = int(prompt("Enter engagement ID to resume: "))
            e = db.get_engagement(eid)
            if e:
                success(f"Resuming: {e['engagement_name']}")
                return eid
        except (ValueError, TypeError):
            pass
        warn("Invalid ID.")
        return None
    return None


def check_target_in_scope(target, engagement_id):
    """
    Returns (True, reason) if target is in scope, (False, reason) if not.
    Checks string containment: a target matches if the stored scope item is
    a substring of the target or vice versa (handles CIDRs loosely).
    """
    scope = db.get_scope_items(engagement_id)
    for item in scope["out_of_scope"]:
        if item["target"].lower() in target.lower() or target.lower() in item["target"].lower():
            return False, f"Target matches out-of-scope item: {item['target']}"
    for item in scope["in_scope"]:
        if item["target"].lower() in target.lower() or target.lower() in item["target"].lower():
            return True, f"Target matches in-scope item: {item['target']}"
    # No explicit scope match — warn but allow
    return True, "Target not explicitly listed in scope — proceed with caution"
