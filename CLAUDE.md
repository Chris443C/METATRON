# Project CLAUDE.md

Read and follow in this order:
1. `.claude/global.md`
2. this `CLAUDE.md`
3. `.claude/commands/*` when invoked

This file contains project-specific rules, repository context, local conventions, and any intentional overrides to the managed global Claude rules.

Do not duplicate generic coding, safety, workflow, or .NET standards already defined in `.claude/global.md` unless this project intentionally overrides them.

---

## 1. Project Context

### 1.1 Core Details
- Project name: METATRON
- Purpose: LLM-powered assistant/agent system with local Ollama model support
- Project type: Python CLI / AI agent
- Primary language and framework: Python
- Solution file: metatron.py (entry point)
- Main application entry points: metatron.py
- Test project locations: (none yet)
- Deployment target: Local / self-hosted
- Key integrations: Ollama (local LLM), DuckDuckGo search, SQLite (db.py)
- Security or compliance sensitivity: Low — local tooling only

### 1.2 Fast Context
Use this section to reduce repeated repo exploration.

- Commonly changed folders: root (all source files are at root level)
- Primary business logic locations: metatron.py, llm.py, tools.py, search.py
- API or UI entry paths: metatron.py (CLI)
- Infrastructure or deployment files usually relevant: Modelfile, requirements.txt
- Files or folders usually out of scope: screenshots/
- Known expensive areas to avoid unless needed: N/A
- Common validation commands if they differ from global defaults: `python metatron.py`

### 1.3 Architecture Summary
- Main modules or services: metatron.py (orchestration), llm.py (LLM calls), tools.py (tool registry), search.py (web search), db.py (persistence), export.py (output)
- High-level data flow: CLI input → metatron.py → llm.py → Ollama API → tool calls via tools.py → response
- External dependencies: Ollama (local), DuckDuckGo search API
- Trust boundaries or sensitive components: All local — no remote data exfiltration paths

---

## 2. Repository-Specific Conventions

- All source files are at the project root (flat structure)
- Python — follow PEP 8
- No test suite exists yet; add tests under `tests/` if introduced
- Modelfile defines the Ollama model configuration for this project

---

## 3. Validation Overrides

- Required restore command: `pip install -r requirements.txt`
- Required build command: N/A (interpreted)
- Required test command: N/A (no tests yet)
- Required format or analyzer checks: N/A
- Additional validation steps: `python metatron.py` smoke test
- Narrowest acceptable validation scope for routine changes: import check + smoke run

---

## 4. Security and Compliance Rules

- This is a local development tool — no production data handling
- Do not hardcode API keys or credentials in source files
- Ollama runs locally; no external LLM API calls unless explicitly added

---

## 5. Local Overrides to Global Rules

- Override: Default language is Python, not C# / .NET
- Rationale: This is a Python project
- Scope: All of this repository

---

## 6. Project Commands

```yaml
language: Python
restore_command: pip install -r requirements.txt
build_command: "N/A"
test_command: "N/A"
format_check_command: "N/A"
```

---

## 7. Efficiency Notes

- Typical task types: feature additions, tool integrations, LLM prompt tuning
- Usual minimum file set for common fixes: metatron.py + the relevant module (llm.py, tools.py, etc.)
- Areas where Claude tends to over-read: screenshots/, unrelated root files
- Common causes of failed first attempts: missing Ollama context, incorrect tool call format
- Local rules that improve first-pass success: read metatron.py and the relevant module before proposing changes
