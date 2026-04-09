#!/usr/bin/env python3

import os
import datetime
import mysql.connector
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER

SEVERITY_COLORS = {
    "critical": "#c0392b",
    "high":     "#e67e22",
    "medium":   "#f1c40f",
    "low":      "#27ae60",
    "unknown":  "#7f8c8d",
}

RISK_COLORS = {
    "CRITICAL": "#c0392b",
    "HIGH":     "#e67e22",
    "MEDIUM":   "#f1c40f",
    "LOW":      "#27ae60",
    "UNKNOWN":  "#7f8c8d",
}


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="metatron",
        password="123",
        database="metatron"
    )


def fetch_session(sl_no: int) -> dict:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM history WHERE sl_no = %s", (sl_no,))
    history = c.fetchone()
    c.execute("SELECT * FROM vulnerabilities WHERE sl_no = %s", (sl_no,))
    vulns = c.fetchall()
    c.execute("SELECT * FROM fixes WHERE sl_no = %s", (sl_no,))
    fixes = c.fetchall()
    c.execute("SELECT * FROM exploits_attempted WHERE sl_no = %s", (sl_no,))
    exploits = c.fetchall()
    c.execute("SELECT * FROM summary WHERE sl_no = %s", (sl_no,))
    summary = c.fetchone()
    conn.close()
    return {"history": history, "vulns": vulns, "fixes": fixes,
            "exploits": exploits, "summary": summary}


def fetch_all_history():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT sl_no, target, scan_date, status FROM history ORDER BY sl_no DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def export_pdf(data: dict, output_dir: str) -> str:
    h        = data["history"]
    sl       = h[0]
    tgt      = h[1]
    date     = str(h[2])
    risk     = data["summary"][4] if data["summary"] else "UNKNOWN"
    ai       = data["summary"][3] if data["summary"] else ""

    os.makedirs(output_dir, exist_ok=True)
    safe = tgt.replace("https://","").replace("http://","").replace("/","_").replace(".","_")
    filename = os.path.join(output_dir, f"metatron_SL{sl}_{safe}.pdf")
    doc      = SimpleDocTemplate(filename, pagesize=A4,
                                  topMargin=15*mm, bottomMargin=15*mm,
                                  leftMargin=15*mm, rightMargin=15*mm)

    title_style  = ParagraphStyle("t",  fontSize=22, fontName="Helvetica-Bold",
                                   textColor=colors.HexColor("#c0392b"), spaceAfter=4)
    sub_style    = ParagraphStyle("s",  fontSize=10, fontName="Helvetica",
                                   textColor=colors.HexColor("#555555"), spaceAfter=2)
    h1_style     = ParagraphStyle("h1", fontSize=13, fontName="Helvetica-Bold",
                                   textColor=colors.HexColor("#2c3e50"),
                                   spaceBefore=10, spaceAfter=4)
    body_style   = ParagraphStyle("b",  fontSize=9,  fontName="Helvetica",
                                   textColor=colors.black, leading=13)
    code_style   = ParagraphStyle("c",  fontSize=7.5, fontName="Courier",
                                   textColor=colors.HexColor("#2c3e50"),
                                   backColor=colors.HexColor("#f4f4f4"),
                                   leading=11, leftIndent=6, rightIndent=6,
                                   spaceBefore=2, spaceAfter=2)
    footer_style = ParagraphStyle("f",  fontSize=7,
                                   textColor=colors.HexColor("#aaaaaa"),
                                   alignment=TA_CENTER)
    story = []

    story.append(Paragraph("METATRON", title_style))
    story.append(Paragraph("AI Penetration Testing Report", sub_style))
    story.append(HRFlowable(width="100%", thickness=1.5,
                             color=colors.HexColor("#c0392b"), spaceAfter=8))

    risk_color = colors.HexColor(RISK_COLORS.get(risk.upper(), "#7f8c8d"))
    meta = [["Target", tgt], ["Scan Date", date],
            ["Session", f"SL# {sl}"], ["Risk Level", risk],
            ["Generated", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]]
    mt = Table(meta, colWidths=[35*mm, 130*mm])
    mt.setStyle(TableStyle([
        ("FONTNAME",       (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE",       (0,0), (-1,-1), 9),
        ("FONTNAME",       (0,0), (0,-1),  "Helvetica-Bold"),
        ("TEXTCOLOR",      (0,0), (0,-1),  colors.HexColor("#2c3e50")),
        ("TEXTCOLOR",      (1,3), (1,3),   risk_color),
        ("FONTNAME",       (1,3), (1,3),   "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.HexColor("#f9f9f9"), colors.white]),
        ("GRID",           (0,0), (-1,-1), 0.3, colors.HexColor("#dddddd")),
        ("PADDING",        (0,0), (-1,-1), 5),
    ]))
    story.append(mt)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Vulnerabilities", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#dddddd"), spaceAfter=6))
    if data["vulns"]:
        vd = [["#", "Vulnerability", "Severity", "Port", "Service"]]
        for v in data["vulns"]:
            vd.append([str(v[0]), str(v[2] or "-"),
                       str(v[3] or "-").upper(), str(v[4] or "-"), str(v[5] or "-")])
        vt  = Table(vd, colWidths=[10*mm, 72*mm, 24*mm, 18*mm, 28*mm], repeatRows=1)
        vts = [
            ("FONTNAME",       (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTSIZE",       (0,0), (-1,-1), 8),
            ("BACKGROUND",     (0,0), (-1,0),  colors.HexColor("#2c3e50")),
            ("TEXTCOLOR",      (0,0), (-1,0),  colors.white),
            ("GRID",           (0,0), (-1,-1), 0.3, colors.HexColor("#dddddd")),
            ("PADDING",        (0,0), (-1,-1), 5),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f9f9f9"), colors.white]),
        ]
        for i, v in enumerate(data["vulns"], 1):
            sc = colors.HexColor(SEVERITY_COLORS.get((v[3] or "unknown").lower(), "#7f8c8d"))
            vts.append(("TEXTCOLOR", (2,i), (2,i), sc))
            vts.append(("FONTNAME",  (2,i), (2,i), "Helvetica-Bold"))
        vt.setStyle(TableStyle(vts))
        story.append(vt)
        story.append(Spacer(1, 6))

        story.append(Paragraph("Vulnerability Details", h1_style))
        story.append(HRFlowable(width="100%", thickness=0.5,
                                 color=colors.HexColor("#dddddd"), spaceAfter=6))
        for v in data["vulns"]:
            sc  = colors.HexColor(SEVERITY_COLORS.get((v[3] or "unknown").lower(), "#7f8c8d"))
            lbl = ParagraphStyle("vl", fontSize=9, fontName="Helvetica-Bold", textColor=sc)
            story.append(Paragraph(f"[{(v[3] or 'UNKNOWN').upper()}] {v[2]}", lbl))
            if v[6]:
                story.append(Paragraph(str(v[6]), body_style))
            story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("No vulnerabilities recorded.", body_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Fixes & Mitigations", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#dddddd"), spaceAfter=6))
    if data["fixes"]:
        for f in data["fixes"]:
            story.append(Paragraph(f"Fix for vuln id={f[2]}:", body_style))
            story.append(Paragraph(str(f[3] or "-"), code_style))
            story.append(Spacer(1, 3))
    else:
        story.append(Paragraph("No fixes recorded.", body_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Exploits Attempted", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#dddddd"), spaceAfter=6))
    if data["exploits"]:
        ed = [["#", "Exploit", "Tool", "Result"]]
        for e in data["exploits"]:
            ed.append([str(e[0]), str(e[2] or "-")[:60],
                       str(e[3] or "-")[:30], str(e[5] or "-")[:30]])
        et = Table(ed, colWidths=[10*mm, 80*mm, 40*mm, 28*mm])
        et.setStyle(TableStyle([
            ("FONTNAME",       (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTSIZE",       (0,0), (-1,-1), 8),
            ("BACKGROUND",     (0,0), (-1,0),  colors.HexColor("#2c3e50")),
            ("TEXTCOLOR",      (0,0), (-1,0),  colors.white),
            ("GRID",           (0,0), (-1,-1), 0.3, colors.HexColor("#dddddd")),
            ("PADDING",        (0,0), (-1,-1), 5),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f9f9f9"), colors.white]),
        ]))
        story.append(et)
    else:
        story.append(Paragraph("No exploits recorded.", body_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("AI Analysis Summary", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#dddddd"), spaceAfter=6))
    if ai:
        for line in str(ai).split("\n"):
            line = line.strip()
            if line:
                story.append(Paragraph(line, body_style))
                story.append(Spacer(1, 2))
    else:
        story.append(Paragraph("No AI analysis recorded.", body_style))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#dddddd"), spaceAfter=4))
    story.append(Paragraph(
        "Generated by METATRON — AI Penetration Testing Assistant | "
        "github.com/sooryathejas/METATRON | For authorized use only.",
        footer_style))

    doc.build(story)
    return filename


def export_html(data: dict, output_dir: str) -> str:
    h    = data["history"]
    sl   = h[0]
    tgt  = h[1]
    date = str(h[2])
    risk = data["summary"][4] if data["summary"] else "UNKNOWN"
    ai   = data["summary"][3] if data["summary"] else ""
    rc   = RISK_COLORS.get(risk.upper(), "#7f8c8d")

    os.makedirs(output_dir, exist_ok=True)
    safe = tgt.replace("https://","").replace("http://","").replace("/","_").replace(".","_")
    filename = os.path.join(output_dir, f"metatron_SL{sl}_{safe}.html")
    vuln_rows = ""
    for v in data["vulns"]:
        sc = SEVERITY_COLORS.get((v[3] or "unknown").lower(), "#7f8c8d")
        vuln_rows += (f"<tr><td>{v[0]}</td>"
                      f"<td><strong>{v[2]}</strong><br><small>{v[6] or ''}</small></td>"
                      f"<td><span style='color:{sc};font-weight:bold'>"
                      f"{(v[3] or 'unknown').upper()}</span></td>"
                      f"<td>{v[4] or '-'}</td><td>{v[5] or '-'}</td></tr>")

    fix_rows = ""
    for f in data["fixes"]:
        fix_rows += (f"<tr><td>{f[0]}</td><td>vuln #{f[2]}</td>"
                     f"<td><code>{f[3] or '-'}</code></td>"
                     f"<td>{f[4] or 'ai'}</td></tr>")

    exp_rows = ""
    for e in data["exploits"]:
        exp_rows += (f"<tr><td>{e[0]}</td><td>{e[2] or '-'}</td>"
                     f"<td>{e[3] or '-'}</td>"
                     f"<td><code>{str(e[4] or '-')[:80]}</code></td>"
                     f"<td>{e[5] or '-'}</td></tr>")

    ai_html = "".join(f"<p>{line}</p>"
                      for line in str(ai).split("\n") if line.strip())

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Metatron Report — {tgt}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',sans-serif;background:#0d0d0d;color:#e0e0e0;padding:30px}}
.container{{max-width:960px;margin:auto}}
.header{{border-left:5px solid #c0392b;padding-left:16px;margin-bottom:30px}}
.header h1{{font-size:2.2em;color:#c0392b}}
.header p{{color:#888;font-size:.95em}}
.meta-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:30px}}
.meta-card{{background:#1a1a1a;border:1px solid #333;border-radius:6px;padding:14px}}
.meta-card .label{{font-size:.75em;color:#888;text-transform:uppercase;margin-bottom:4px}}
.meta-card .value{{font-size:1.1em;font-weight:bold}}
.risk{{color:{rc}}}
section{{margin-bottom:30px}}
section h2{{font-size:1.2em;color:#c0392b;border-bottom:1px solid #333;
            padding-bottom:8px;margin-bottom:14px}}
table{{width:100%;border-collapse:collapse;font-size:.88em}}
th{{background:#1e1e1e;color:#aaa;text-align:left;padding:10px;
    font-size:.8em;text-transform:uppercase;border-bottom:2px solid #333}}
td{{padding:10px;border-bottom:1px solid #222;vertical-align:top}}
tr:hover td{{background:#1a1a1a}}
code{{background:#1e1e1e;padding:2px 6px;border-radius:3px;
      font-family:monospace;font-size:.85em;color:#e74c3c}}
.ai-box{{background:#111;border:1px solid #333;border-radius:6px;
         padding:16px;font-size:.9em;line-height:1.7;color:#ccc}}
.ai-box p{{margin-bottom:8px}}
.footer{{text-align:center;color:#444;font-size:.78em;
         margin-top:40px;border-top:1px solid #222;padding-top:16px}}
a{{color:#555}}
</style>
</head>
<body>
<div class="container">

<div class="header">
  <h1>🔱 METATRON</h1>
  <p>AI Penetration Testing Report</p>
</div>

<div class="meta-grid">
  <div class="meta-card">
    <div class="label">Target</div>
    <div class="value">{tgt}</div>
  </div>
  <div class="meta-card">
    <div class="label">Session</div>
    <div class="value">SL# {sl}</div>
  </div>
  <div class="meta-card">
    <div class="label">Scan Date</div>
    <div class="value">{date}</div>
  </div>
  <div class="meta-card">
    <div class="label">Risk Level</div>
    <div class="value risk">{risk}</div>
  </div>
</div>

<section>
  <h2>Vulnerabilities</h2>
  {'<table><thead><tr><th>#</th><th>Vulnerability</th><th>Severity</th><th>Port</th><th>Service</th></tr></thead><tbody>' + vuln_rows + '</tbody></table>' if data["vulns"] else '<p style="color:#888">None recorded.</p>'}
</section>

<section>
  <h2>Fixes &amp; Mitigations</h2>
  {'<table><thead><tr><th>#</th><th>Vuln</th><th>Fix</th><th>Source</th></tr></thead><tbody>' + fix_rows + '</tbody></table>' if data["fixes"] else '<p style="color:#888">None recorded.</p>'}
</section>

<section>
  <h2>Exploits Attempted</h2>
  {'<table><thead><tr><th>#</th><th>Exploit</th><th>Tool</th><th>Payload</th><th>Result</th></tr></thead><tbody>' + exp_rows + '</tbody></table>' if data["exploits"] else '<p style="color:#888">None recorded.</p>'}
</section>

<section>
  <h2>AI Analysis Summary</h2>
  <div class="ai-box">
    {ai_html if ai_html else '<p style="color:#888">None recorded.</p>'}
  </div>
</section>

<div class="footer">
  Generated by METATRON &mdash;
  <a href="https://github.com/sooryathejas/METATRON">github.com/sooryathejas/METATRON</a>
  &mdash; For authorized use only.
</div>

</div>
</body>
</html>"""

    with open(filename, "w") as f:
        f.write(html)
    return filename


def export_menu(data: dict):
    if not data["history"]:
        print("[!] No session data to export.")
        return

    h   = data["history"]
    sl  = h[0]
    tgt = h[1]

    print(f"\n\033[33m{'─'*20} EXPORT SL#{sl} — {tgt} {'─'*20}\033[0m")
    print("  [1] PDF report")
    print("  [2] HTML report")
    print("  [3] Both")
    print("  [4] Back")
    print(f"\033[90m{'─'*60}\033[0m")

    choice     = input("\033[36mExport format: \033[0m").strip()
    output_dir = os.path.expanduser("~/METATRON/reports")
    os.makedirs(output_dir, exist_ok=True)

    if choice == "1":
        p = export_pdf(data, output_dir)
        print(f"\033[92m[+] PDF saved: {p}\033[0m")
    elif choice == "2":
        p = export_html(data, output_dir)
        print(f"\033[92m[+] HTML saved: {p}\033[0m")
    elif choice == "3":
        p1 = export_pdf(data, output_dir)
        p2 = export_html(data, output_dir)
        print(f"\033[92m[+] PDF  : {p1}\033[0m")
        print(f"\033[92m[+] HTML : {p2}\033[0m")
    elif choice == "4":
        return
    else:
        print("\033[93m[!] Invalid choice.\033[0m")


if __name__ == "__main__":
    print("\n\033[91m    METATRON — Standalone Report Exporter\033[0m")
    print("\033[90m    ─────────────────────────────────────\033[0m\n")

    rows = fetch_all_history()
    if not rows:
        print("[!] No sessions found in database.")
        exit()

    print(f"{'SL#':<6} {'TARGET':<28} {'DATE':<22} {'STATUS'}")
    print("─" * 65)
    for row in rows:
        print(f"{row[0]:<6} {row[1]:<28} {str(row[2]):<22} {row[3]}")
    print()

    sl_input = input("\033[36mEnter SL# to export: \033[0m").strip()
    if not sl_input.isdigit():
        print("[!] Invalid SL#.")
        exit()

    data = fetch_session(int(sl_input))
    if not data["history"]:
        print(f"[!] SL# {sl_input} not found.")
        exit()

    export_menu(data)


# ─────────────────────────────────────────────
# PROFESSIONAL REPORT FUNCTIONS
# ─────────────────────────────────────────────

def build_evidence_appendix(evidence_list):
    """Build reportlab story elements for evidence appendix."""
    from reportlab.platypus import Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    styles = getSampleStyleSheet()
    story = []
    for ev in evidence_list:
        story.append(Paragraph(f"<b>Evidence: {ev.get('label', 'unnamed')}</b>",
                               styles['Normal']))
        story.append(Paragraph(
            f"Phase: {ev.get('phase', '')} | "
            f"Type: {ev.get('evidence_type', '')} | "
            f"Captured: {ev.get('captured_at', '')}",
            styles['Normal']
        ))
        content = str(ev.get("content", ""))[:2000]
        story.append(Paragraph(f"<pre>{content}</pre>", styles['Code']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
        story.append(Spacer(1, 4 * mm))
    return story


def _add_cloud_section_to_pdf(story, cloud_findings, styles):
    """Add cloud findings section to a reportlab story list."""
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    if not cloud_findings:
        story.append(Paragraph("No cloud findings recorded.", styles["Normal"]))
        return
    SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"]
    sorted_findings = sorted(
        cloud_findings,
        key=lambda f: (SEVERITY_ORDER.index(f.get("severity", "info")),
                       f.get("provider", ""))
    )
    tdata = [["#", "Provider", "Service", "Finding", "Severity", "Resource"]]
    for i, f in enumerate(sorted_findings, 1):
        tdata.append([
            str(i),
            str(f.get("provider", "")).upper(),
            str(f.get("service", "")),
            str(f.get("finding_title", ""))[:45],
            str(f.get("severity", "")).upper(),
            str(f.get("resource_id", ""))[:30],
        ])
    t = Table(tdata, colWidths=[8*mm, 18*mm, 22*mm, 65*mm, 22*mm, 35*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
    ]))
    story.append(t)
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("<b>Critical and High Findings Detail:</b>", styles["Normal"]))
    for f in sorted_findings:
        if f.get("severity") not in ("critical", "high"):
            continue
        story.append(Paragraph(
            f"<b>{str(f.get('provider','')).upper()} — {f.get('finding_title','')} "
            f"({str(f.get('severity','')).upper()})</b>",
            styles["Normal"]
        ))
        if f.get("description"):
            story.append(Paragraph(f"Finding: {f['description'][:500]}", styles["Normal"]))
        if f.get("recommendation"):
            story.append(Paragraph(f"Recommendation: {f['recommendation'][:300]}", styles["Normal"]))
        story.append(Spacer(1, 2*mm))


def _add_segmentation_section_to_pdf(story, seg_tests, styles):
    """Add PCI 11.4.5 segmentation testing section to a reportlab story list."""
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    story.append(Paragraph(
        "PCI DSS Requirement 11.4.5 — Segmentation Validation Testing",
        styles["Heading2"]
    ))
    if not seg_tests:
        story.append(Paragraph("No segmentation tests recorded for this engagement.", styles["Normal"]))
        return
    pass_count = sum(1 for t in seg_tests if t.get("result") == "PASS")
    fail_count = sum(1 for t in seg_tests if t.get("result") == "FAIL")
    compliance = "COMPLIANT" if fail_count == 0 else "NON-COMPLIANT"
    story.append(Paragraph(
        f"Overall Compliance: <b>{compliance}</b> — {pass_count} PASS / {fail_count} FAIL",
        styles["Normal"]
    ))
    story.append(Spacer(1, 3*mm))
    tdata = [["Source", "Destination", "Port", "Protocol", "Expected", "Result", "Tool", "Date"]]
    for t in seg_tests:
        tdata.append([
            str(t.get("source_host", ""))[:22],
            str(t.get("dest_host", ""))[:22],
            str(t.get("dest_port", "")),
            str(t.get("protocol", "tcp")).upper(),
            str(t.get("expected", "")).upper(),
            str(t.get("result", "ERROR")),
            str(t.get("tool_used", ""))[:10],
            str(t.get("tested_at", ""))[:10] if t.get("tested_at") else "",
        ])
    t_table = Table(tdata, colWidths=[30*mm, 30*mm, 12*mm, 16*mm, 18*mm, 14*mm, 15*mm, 22*mm])
    table_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]
    for row_idx, t in enumerate(seg_tests, start=1):
        if t.get("result") == "FAIL":
            table_style.append(("BACKGROUND", (5, row_idx), (5, row_idx),
                                 colors.HexColor("#fde8e8")))
        else:
            table_style.append(("BACKGROUND", (5, row_idx), (5, row_idx),
                                 colors.HexColor("#e8fde8")))
    t_table.setStyle(TableStyle(table_style))
    story.append(t_table)
    story.append(Spacer(1, 3*mm))
    tester_names = list({t.get("tester_name", "unknown") for t in seg_tests if t.get("tester_name")})
    story.append(Paragraph(
        f"Tester: {', '.join(tester_names)} | Tool chain: ncat → nc → python_socket",
        styles["Normal"]
    ))


def export_professional_pdf(engagement_data, output_dir, include_pci=False):
    """
    Full professional PDF report covering all 10 phases of data.
    engagement_data: dict with keys 'engagement' and 'sessions'.
    Returns output file path.
    """
    import os
    import db as _db
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, HRFlowable, PageBreak)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    e = engagement_data.get("engagement", {})
    sessions = engagement_data.get("sessions", [])
    all_vulns, all_exploits, all_post_exploit, all_attack_paths, all_evidence = [], [], [], [], []
    for s in sessions:
        sl_no = s["history"][0]
        all_vulns.extend(s.get("vulnerabilities", []))
        all_exploits.extend(s.get("exploits", []))
        all_post_exploit.extend(_db.get_post_exploitation(sl_no))
        all_attack_paths.extend(_db.get_attack_paths(sl_no))
        all_evidence.extend(_db.get_evidence(sl_no))
    cloud_findings = _db.get_cloud_findings(sessions[0]["history"][0]) if sessions else []
    seg_tests = _db.get_segmentation_tests(sessions[0]["history"][0]) if sessions else []
    os.makedirs(output_dir, exist_ok=True)
    client_safe = "".join(c if c.isalnum() else "_" for c in e.get("client_name", "unknown"))
    filename = os.path.join(output_dir, f"metatron_professional_{client_safe}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=25*mm, bottomMargin=25*mm)
    styles = getSampleStyleSheet()
    H1 = ParagraphStyle("H1", parent=styles["Heading1"], textColor=colors.HexColor("#c0392b"))
    H2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=colors.HexColor("#2c3e50"))
    story = []
    # Cover
    story.append(Spacer(1, 30*mm))
    story.append(Paragraph("PENETRATION TEST REPORT", H1))
    story.append(Paragraph(e.get("engagement_name", ""), styles["Heading2"]))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(f"Client: {e.get('client_name', '')}", styles["Normal"]))
    story.append(Paragraph(f"Test Type: {e.get('test_type', '')} box", styles["Normal"]))
    story.append(Paragraph(
        f"Dates: {e.get('start_date', '')} — {e.get('end_date', '')}", styles["Normal"]
    ))
    story.append(PageBreak())
    # Executive Summary
    story.append(Paragraph("Executive Summary", H1))
    exec_summary = next(
        (ev.get("content", "") for ev in all_evidence if ev.get("label") == "Executive Summary"),
        "Executive summary not generated. Run Phase 7 to generate."
    )
    story.append(Paragraph(exec_summary, styles["Normal"]))
    story.append(PageBreak())
    # Scope
    story.append(Paragraph("Scope & Methodology", H1))
    scope = _db.get_scope_items(e.get("id", 0)) if e.get("id") else {"in_scope": [], "out_of_scope": []}
    story.append(Paragraph("<b>In Scope:</b>", styles["Normal"]))
    for s in scope["in_scope"]:
        story.append(Paragraph(f"• {s['target']} — {s.get('description', '')}", styles["Normal"]))
    story.append(Paragraph("<b>Out of Scope:</b>", styles["Normal"]))
    for s in scope["out_of_scope"]:
        story.append(Paragraph(f"• {s['target']}", styles["Normal"]))
    story.append(PageBreak())
    # Findings Summary
    story.append(Paragraph("Findings Summary", H1))
    if all_vulns:
        tdata = [["#", "Vulnerability", "Severity", "Port", "Service"]]
        for i, v in enumerate(all_vulns, 1):
            tdata.append([str(i), str(v[2])[:40], str(v[3]), str(v[4]), str(v[5])])
        t = Table(tdata, colWidths=[10*mm, 80*mm, 25*mm, 20*mm, 35*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("No vulnerabilities recorded.", styles["Normal"]))
    # Attack Paths
    if all_attack_paths:
        story.append(PageBreak())
        story.append(Paragraph("Attack Paths", H1))
        for ap in all_attack_paths:
            story.append(Paragraph(
                f"<b>{ap['path_name']}</b> ({str(ap['severity']).upper()})", H2
            ))
            story.append(Paragraph(ap.get("ai_narrative", ""), styles["Normal"]))
            for i, step in enumerate(ap.get("steps", []), 1):
                story.append(Paragraph(f"Step {i}: {step}", styles["Normal"]))
            story.append(Spacer(1, 3*mm))
    # Post-Exploitation
    if all_post_exploit:
        story.append(PageBreak())
        story.append(Paragraph("Post-Exploitation Findings", H1))
        for pe in all_post_exploit:
            status = "SUCCESS" if pe.get("success") else "ATTEMPTED"
            story.append(Paragraph(
                f"<b>{pe['technique']}</b> — {pe['technique_type']} [{status}]", H2
            ))
            story.append(Paragraph(
                f"{pe.get('from_user', '')} on {pe.get('from_host', '')} → "
                f"{pe.get('to_user', '')} on {pe.get('to_host', '')}",
                styles["Normal"]
            ))
            if pe.get("evidence_notes"):
                story.append(Paragraph(pe["evidence_notes"][:500], styles["Normal"]))
    # Cloud Findings
    if cloud_findings:
        story.append(PageBreak())
        story.append(Paragraph("Cloud Security Findings", H1))
        _add_cloud_section_to_pdf(story, cloud_findings, styles)
    # Segmentation Testing
    if seg_tests:
        story.append(PageBreak())
        story.append(Paragraph("Network Segmentation Testing", H1))
        _add_segmentation_section_to_pdf(story, seg_tests, styles)
    # Evidence Appendix
    if all_evidence:
        story.append(PageBreak())
        story.append(Paragraph("Evidence Appendix", H1))
        story.extend(build_evidence_appendix(all_evidence))
    # PCI DSS Appendix
    if include_pci:
        story.append(PageBreak())
        story.append(Paragraph("PCI DSS 4.0.1 Mapping", H1))
        pci_rows = [
            ["Requirement", "Coverage", "Notes"],
            ["11.4.1 External Penetration Test", "Covered", "External targets tested per scope"],
            ["11.4.2 Internal Penetration Test", "See scope", "Internal testing if in scope"],
            ["11.4.3 Segmentation Testing", "See scope", "Add segmentation test results here"],
            ["11.4.4 Pentest Corrections", "Remediation required", "See findings for required fixes"],
        ]
        t = Table(pci_rows, colWidths=[70*mm, 35*mm, 65*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ]))
        story.append(t)
    doc.build(story)
    return filename


def export_retest_report_pdf(original_data, retest_data, comparison, output_dir):
    """Retest comparison PDF report."""
    import os
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle)
    from reportlab.lib.styles import getSampleStyleSheet
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir,
                            f"metatron_retest_SL{original_data['history'][0]}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=25*mm, bottomMargin=25*mm)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("RETEST REPORT", styles["Heading1"]))
    story.append(Paragraph(
        f"Original scan: SL#{original_data['history'][0]} | "
        f"Target: {original_data['history'][1]} | "
        f"Date: {original_data['history'][2]}",
        styles["Normal"]
    ))
    story.append(Paragraph(
        f"Remediation score: {comparison.get('remediation_score', 0)}%",
        styles["Heading2"]
    ))
    story.append(Spacer(1, 5*mm))
    tdata = [["Vulnerability", "Original Severity", "Status"]]
    STATUS_ICONS = {"FIXED": "✓ FIXED", "PARTIAL": "~ PARTIAL",
                    "NOT_FIXED": "✗ NOT FIXED", "NOT_TESTED": "? NOT TESTED"}
    for fc in comparison.get("findings_comparison", []):
        tdata.append([
            str(fc["vuln_name"])[:50],
            str(fc.get("original_severity", "")),
            STATUS_ICONS.get(fc["status"], fc["status"]),
        ])
    t = Table(tdata, colWidths=[90*mm, 35*mm, 45*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(comparison.get("retest_summary", ""), styles["Normal"]))
    doc.build(story)
    return filename
