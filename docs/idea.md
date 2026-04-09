What are the standard stages of pentesting? 

The standard penetration testing methodology typically follows 6–8 structured phases. These stages are used by frameworks like:

PTES
NIST (NIST SP 800-115)
OWASP
CREST

Below are the industry-standard stages used by professional pentesters.

Standard Pentesting Stages
1. Pre-Engagement / Planning

This is where scope and rules are defined.

Activities

Define scope (IPs, domains, apps, cloud, APIs)
Define testing type (Black / Grey / White box)
Legal authorization / Rules of Engagement
Define testing windows
Define data handling requirements

Outputs

Rules of Engagement (RoE)
Scope document
Risk acceptance

This phase is critical for PCI DSS assessments (something you're very familiar with).

2. Reconnaissance (Information Gathering)

Also called OSINT / Footprinting

Passive Recon

DNS records
WHOIS
Public GitHub repos
LinkedIn employees
Technology fingerprinting

Active Recon

Port scanning
Service detection
Subdomain discovery
Cloud asset discovery

Tools

Nmap
Amass
Subfinder
Shodan
theHarvester
3. Scanning & Enumeration

Now the tester begins identifying attack surface and vulnerabilities

Activities

Port scanning
Service enumeration
Version detection
Directory brute forcing
Vulnerability scanning

Examples

SMB enumeration
LDAP enumeration
API discovery
Cloud misconfiguration checks

Tools

Nmap
Nessus
Burp Suite (you mentioned you have Professional)
Nikto
Dirsearch
4. Vulnerability Analysis

Now findings are validated and prioritized.

Activities

Identify exploitable vulnerabilities
Remove false positives
Chain vulnerabilities together
Determine attack paths

This is where real pentesting starts vs just scanning.

Example:

Weak password + exposed RDP
SSRF → internal metadata service → credential theft
5. Exploitation

This is the actual compromise phase.

Activities

Gain access to systems
Exploit vulnerabilities
Bypass controls
Capture credentials
Access sensitive data

Examples:

Reverse shells
SQL Injection
Authentication bypass
Privilege escalation

Tools:

Metasploit
Burp Suite
custom exploits
manual testing
6. Post-Exploitation

Once access is gained, testers determine impact.

Activities

Privilege escalation
Lateral movement
Persistence testing
Data exfiltration simulation
Domain compromise

Example:

User access → Domain Admin
Web server → database → production systems

This phase answers:

"What could an attacker actually do?"

7. Reporting

This is one of the most important phases (especially for PCI DSS).

Includes

Executive summary
Technical findings
Risk ratings
Proof of concept
Remediation guidance

Typical Structure:

Executive Summary
Scope
Methodology
Findings
Risk ratings
Recommendations
8. Retesting (Optional but Recommended)

After remediation:

Validate fixes
Confirm vulnerabilities resolved
Provide updated report

Often required for:

PCI DSS
ISO 27001
Cyber Essentials Plus
The Simple 6-Stage Model (Common Summary)

Most pentests follow:

Planning
Reconnaissance
Scanning / Enumeration
Exploitation
Post-Exploitation
Reporting
Real-World Pentest Types (These stages apply to all)
External Network Pentest
Internal Pentest
Web Application Pentest
API Pentest
Cloud Pentest
Red Team Exercise
Wireless Pentest
How Red Team Differs Slightly

Red Teams also include:

Initial access simulation
Phishing
Social engineering
Physical access
For Your Use Case (Burp + Local AI + Pentesting Stack)

Since you're building:

Local LLM pentesting tools
Burp Suite integration
METATRON / Ollama environment

You would typically automate:

Recon
Enumeration
Vulnerability analysis

And keep exploitation manual.

That's exactly how modern AI-assisted pentesting is evolving.

If you'd like, I can also provide:

A Professional Pentest Workflow
A PCI-aligned Pentest Methodology
A Burp Suite-centric workflow
A Local AI-assisted pentest architecture

Just tell me.

All 4 please 

Here are the four pentesting frameworks/workflows tailored to your environment and goals:

Professional Pentest Workflow
PCI-Aligned Pentest Methodology
Burp Suite-Centric Workflow
Local AI-Assisted Pentest Architecture (Your METATRON / Ollama direction)
1. Professional Pentest Workflow (Industry Standard)

This is the CREST / PTES-style workflow used by professional consultancies.

Phase 1 — Pre-Engagement

Define:

Scope (IPs, domains, APIs, cloud, mobile)
Testing type (Black / Grey / White box)
Time windows
Rules of engagement
Out-of-scope systems

Output:

Scope document
Rules of engagement
Risk acceptance
Phase 2 — Reconnaissance
Passive Recon
DNS records
Subdomains
Public repos
Email addresses
Technology stack

Tools:

Amass
Subfinder
theHarvester
Shodan
Phase 3 — Enumeration

Identify attack surface:

Port scanning
Service enumeration
Web directory discovery
API discovery
Cloud exposure

Tools:

Nmap
Masscan
Dirsearch
FFUF
Phase 4 — Vulnerability Analysis

Identify:

Weak configurations
Missing patches
Logic flaws
Authentication weaknesses

Examples:

Default credentials
Weak TLS config
Misconfigured S3 buckets
Broken access control
Phase 5 — Exploitation

Attempt compromise:

SQL injection
RCE
Auth bypass
Credential reuse

Tools:

Burp Suite
Metasploit
Custom scripts
Phase 6 — Post-Exploitation

Determine impact:

Privilege escalation
Lateral movement
Data access
Persistence
Phase 7 — Reporting

Deliver:

Executive summary
Risk ratings
Technical findings
Remediation guidance
2. PCI-Aligned Pentest Methodology

This aligns with PCI DSS v4.0.1 Requirements:

11.4.1 — External Pentesting
11.4.2 — Internal Pentesting
11.4.3 — Segmentation Testing
11.3 — Vulnerability scanning (supporting)

This is particularly relevant to your QSA work.

Phase 1 — Scoping (PCI-Specific)

Define:

CDE systems
Connected-to systems
Security impact systems
Segmentation boundaries

Outputs:

Data flow diagrams
Asset inventory
Scope matrix
Phase 2 — External Pentest

Test:

Internet-facing systems
Payment pages
APIs
VPN portals

Examples:

WAF bypass
Auth bypass
API access
Phase 3 — Internal Pentest

Simulate attacker inside corporate network:

Test:

Domain escalation
Flat networks
Weak segmentation

Example:

User workstation → Domain Admin → CDE

Phase 4 — Segmentation Testing

Critical for PCI:

Verify:

Corporate network cannot access CDE
Guest WiFi isolated
Admin networks controlled

Test methods:

Port scanning
Firewall bypass attempts
Routing validation
Phase 5 — Exploitation

Demonstrate:

Access to CHD environment
Access to payment systems
Access to logging systems
Phase 6 — Evidence Collection

Required for PCI:

Screenshots
Commands
Proof of access
Risk explanation
Phase 7 — PCI Reporting

Deliverables:

Executive summary
Technical findings
Scope validation
Segmentation validation
3. Burp Suite-Centric Pentesting Workflow

This is how professional web app pentesting typically runs.

Phase 1 — Proxy Setup

Configure:

Browser → Burp Proxy
TLS interception
Scope definition
Phase 2 — Crawl / Discovery

Use:

Burp Spider
Manual browsing
API discovery

Identify:

Endpoints
Parameters
Hidden functions
Phase 3 — Passive Scanning

Burp automatically identifies:

Missing headers
Cookie issues
TLS issues
CORS issues
Phase 4 — Active Scanning

Run:

Burp Scanner
Targeted scans
Authenticated scans
Phase 5 — Manual Testing

Critical phase:

Test:

IDOR
Business logic flaws
Privilege escalation
Payment manipulation
Phase 6 — Intruder / Repeater

Use:

Intruder (fuzzing)
Repeater (manual exploitation)
Comparer
Phase 7 — Extensions

Recommended Burp Extensions:

Autorize
JWT Editor
Param Miner
Turbo Intruder
Logger++

Since you have Burp Professional, you already have a strong base.

4. Local AI-Assisted Pentest Architecture (Your METATRON Direction)

This is where your Ollama + Local AI + Burp + Pentesting stack comes in.

Your Architecture:

Burp Suite
     |
Traffic Export
     |
METATRON
     |
Local LLM (Ollama)
     |
Analysis Engine
     |
Attack Suggestions
Stage 1 — Data Collection

Sources:

Burp traffic
Nmap scans
Directory brute force
Cloud enumeration
Stage 2 — AI Analysis

Local LLM analyzes:

API patterns
Auth flows
Hidden endpoints
Logic flaws

Example:

AI detects:

Admin endpoint
Role parameter
Potential privilege escalation
Stage 3 — Attack Generation

AI suggests:

Test cases
Payloads
Fuzzing strategies

Example:

Try:

role=user
role=admin
role=superadmin
Stage 4 — Automated Testing

Your AI tool can:

Generate Burp requests
Generate scripts
Suggest exploitation paths
Stage 5 — Correlation Engine

AI correlates:

Nmap results
Web app findings
Cloud misconfigurations

Example:

Open admin port
Weak API
Internal exposure
Stage 6 — Reporting Engine

Generate:

Pentest report
Attack path diagrams
Risk scoring
Your Ideal Stack (Based on Your Current Setup)

You already have:

Ollama
Burp Professional
Linux VM
Local AI experimentation

Recommended Additions:

Nmap
FFUF
Amass
httpx
nuclei
Metasploit
What You're Building (Advanced Capability)

You're effectively building:

AI Pentesting Assistant
Local Pentest Automation
Red Team Assistant

This is very cutting-edge right now.

If you'd like, I can also:

Help you build METATRON architecture
Configure Burp integration
Add Burp MCP / AI tools
Build full pentest automation stack

Just tell me and we'll build it step-by-step.

All 4

Below are all four in a more practical, usable form.

1. Professional pentest workflow

This is the standard consultancy-style flow for a normal network, internal, external, or application test.

Stage 1: Pre-engagement

Set the scope, objectives, legal authority, constraints, and success criteria.

What gets defined:

in-scope targets
test type: black box, grey box, white box
production safeguards
permitted hours
contact and escalation points
evidence handling rules

Typical outputs:

rules of engagement
scope statement
test plan
risk acknowledgement
Stage 2: Reconnaissance

Collect information about the target before doing intrusive testing.

Passive recon:

domains, subdomains, DNS
public IP ranges
email formats
exposed tech stack
cloud footprint
leaked credentials or repos

Active recon:

host discovery
port scanning
banner grabbing
web fingerprinting

Goal:
Build the target map before touching exploitation.

Stage 3: Enumeration

Move from “what exists” to “what is actually exposed and usable”.

Examples:

enumerate SMB shares
identify LDAP structure
find admin portals
identify API routes
enumerate web directories and parameters
identify authentication methods

Goal:
Understand entry points and trust boundaries.

Stage 4: Vulnerability analysis

Validate weaknesses and filter out scanner noise.

Activities:

confirm versions and exposures
test auth weaknesses
review misconfigurations
identify chaining opportunities
separate false positives from exploitable issues

Goal:
Turn raw findings into realistic attack paths.

Stage 5: Exploitation

Attempt controlled exploitation of validated weaknesses.

Examples:

SQL injection
command injection
authentication bypass
SSRF
credential reuse
insecure deserialisation
local privilege escalation

Goal:
Demonstrate whether the issue is real and what access it grants.

Stage 6: Post-exploitation

Assess impact after initial compromise.

Activities:

privilege escalation
pivoting
lateral movement
sensitive data access
persistence checks, if allowed
segmentation bypass attempts

Goal:
Show business impact, not just technical exploitability.

Stage 7: Reporting

Translate the test into something management and engineers can act on.

A good report includes:

executive summary
methodology
scope and limitations
attack narrative
risk-ranked findings
evidence
remediation advice
Stage 8: Retest

Re-validate fixes and confirm closure.

2. PCI-aligned pentest methodology

This is the same underlying discipline, but driven by PCI DSS scoping and assurance needs. In your world, this matters because the pentest is not just “find bugs”, it is also “validate scope, exposure, and segmentation”.

Stage 1: PCI scoping and boundary definition

Before testing, define:

CDE systems
connected-to systems
security-impacting systems
segmentation controls
payment channels
third-party dependencies
administrative access paths

Key evidence:

network diagrams
data flow diagrams
asset inventory
segmentation description
inbound and outbound trust paths
Stage 2: External pentest

Assess internet-facing exposure that could affect the CDE or related systems.

Typical targets:

VPNs
remote admin portals
payment pages
APIs
public web apps
edge devices
cloud front ends

Questions answered:

can an attacker gain foothold from the internet?
can internet-facing weaknesses reach the CDE, connected-to, or security-impacting systems?
Stage 3: Internal pentest

Assume the attacker is already inside the internal estate.

Test for:

weak internal trust
flat networks
weak admin controls
poor credential hygiene
insecure management interfaces
weak AD posture
insecure jump paths into the CDE

Questions answered:

can a compromised internal device lead to the CDE?
can internal access defeat the intended controls?
Stage 4: Segmentation testing

This is the PCI-critical piece where segmentation is relied on to reduce scope.

Typical tests:

scan from out-of-scope to in-scope segments
test firewall enforcement
test routing and ACL paths
validate denied services
attempt management plane access
test allowed paths for over-permissiveness

Questions answered:

is segmentation genuinely effective?
are “out-of-scope” systems truly isolated from the CDE?
Stage 5: Exploitation and controlled validation

Exploit only enough to prove:

access path exists
scope assumptions are wrong, or confirmed
sensitive systems can or cannot be reached
admin access routes are appropriately restricted
Stage 6: Evidence capture

For PCI, evidence quality matters nearly as much as technical quality.

Capture:

source and destination of tests
screenshots
command output
timestamps
blocked versus allowed flows
proof of segmentation success or failure
proof of access to sensitive assets where relevant
Stage 7: PCI-focused reporting

Your output should clearly cover:

test scope
methodology
assumptions
segmentation validation approach
findings
impact on PCI scope
remediation priorities
retest requirements

A strong PCI pentest report helps support:

Req. 11.4 testing
segmentation reliance
scoping justification
ROC narrative
3. Burp Suite-centric workflow

This is the practical web and API testing workflow when Burp is your main operating console.

Stage 1: Setup and scope control

Configure:

Burp proxy
browser trust store
project file
target scope
authenticated sessions
exclusion rules to avoid noise or breaking flows

Key principle:
Get the application into Burp properly before scanning anything.

Stage 2: Mapping the application

Browse the app manually and let Burp build the target map.

Focus on:

functionality
roles
workflows
APIs
hidden parameters
file upload points
admin-only paths
payment or sensitive transaction flows

Tools used:

Proxy
HTTP history
Target site map
Logger
Repeater

Goal:
Understand how the application actually behaves.

Stage 3: Passive analysis

Let Burp observe the traffic and identify low-risk issues automatically.

Useful for:

cookie flags
cache headers
server disclosures
CORS misconfigurations
CSP weakness
TLS observations
suspicious input reflection

Goal:
Collect easy wins without touching exploitation yet.

Stage 4: Active scanning

Run targeted scans, not indiscriminate ones.

Best practice:

scope tightly
authenticate properly
separate dev, test, and prod where possible
scan feature areas in batches
avoid wasteful full-site scans until mapping is done

Burp Pro shines here for:

injection checks
missing controls
auth-related issues
deserialisation hints
request smuggling indicators
access control edge cases
Stage 5: Manual verification

This is where the real quality comes from.

Use:

Repeater for controlled tests
Intruder for parameter fuzzing
Comparer for response deltas
Decoder for tokens, JWTs, encoded payloads

Manually test:

IDOR/BOLA
vertical privilege escalation
horizontal access control
business logic flaws
workflow bypass
price or transaction tampering
trust of client-side controls
Stage 6: Extension-assisted testing

Common high-value extensions include:

Param Miner
JWT Editor
Autorize
Turbo Intruder
Logger++
Content Type Converter

Use extensions to accelerate, not replace, manual judgement.

Stage 7: Evidence and reporting

For each finding, capture:

affected request
manipulated parameter or sequence
observed response
proof of impact
remediation guidance

A good Burp-led finding should show:

what was changed
what should have happened
what actually happened
why that matters
4. Local AI-assisted pentest architecture

This is the forward-looking model for the sort of stack you have been building around Ollama, local tooling, Burp, and analysis pipelines.

The right way to think about this is not “AI does the pentest”. It is “AI reduces analyst waste, highlights attack paths, and drafts high-value tests”.

Stage 1: Data ingestion

Feed the platform with structured security telemetry.

Good inputs:

Burp traffic exports
Nmap XML
ffuf output
nuclei results
screenshots
HTTP response bodies
OpenAPI specs
directory enumeration results
auth flow notes
cloud exposure data

Goal:
Centralise raw evidence into a format the model can reason over.

Stage 2: Normalisation and indexing

Convert messy tool output into structured objects.

Normalise into things like:

hosts
ports
services
endpoints
parameters
auth methods
roles
response codes
technology fingerprints
suspected weaknesses

This is where a local SQLite or document store helps.

Stage 3: AI-assisted pattern analysis

Use the local model to identify:

likely attack surfaces
repeated auth patterns
suspicious parameter names
admin-only endpoints
inconsistent authorisation behaviour
workflow trust assumptions
likely vulnerability chains

Examples:

same endpoint behaves differently by role token
API exposes internal object identifiers
privileged routes appear in JavaScript but not nav menus
upload function may allow parser abuse
reset flow trusts email parameter without server-side binding
Stage 4: Test case generation

The model proposes targeted tests rather than generic noise.

Examples:

try object ID swapping on these six endpoints
test role manipulation on these JWT claims
compare responses when removing this hidden parameter
fuzz numeric references around invoice and receipt objects
replay multi-step payment flow with altered amount or state token

Goal:
Generate analyst-grade next steps, not autonomous chaos.

Stage 5: Human-led validation

The tester reviews and executes the best suggestions.

This matters because:

models hallucinate
security testing needs judgement
legal scope matters
business logic needs context
exploitation still requires operator control

The AI should assist triage and depth, not take uncontrolled actions.

Stage 6: Correlation and attack path building

This is where local AI becomes genuinely useful.

It can correlate:

host exposure from Nmap
web findings from Burp
secrets or identifiers from JS
auth weaknesses from API behaviour
internal path possibilities from routing data

Example attack path:
Public admin panel exposed → weak password reset logic → low-privileged account access → IDOR to customer records → internal admin function discovery.

Stage 7: Report drafting and remediation support

The model can help draft:

analyst notes
finding summaries
reproduction steps
remediation options
client-ready narrative
retest checklist

Best use:
You provide the verified facts, the model accelerates clean output.

Best way to combine all four

The cleanest model is:

Professional workflow gives the overall structure.
PCI workflow gives scope discipline and evidence standards.
Burp workflow drives web and API testing.
Local AI workflow reduces noise and speeds analysis.

In practice:

use the professional model as the master methodology
overlay PCI where the engagement is compliance-driven
use Burp as the primary web testing console
use local AI for triage, test suggestion, correlation, and draft reporting
Practical one-line summary of each

Professional pentest workflow: the full end-to-end methodology.
PCI-aligned pentest methodology: the compliance-focused version with heavy emphasis on scope and segmentation.
Burp Suite-centric workflow: the hands-on process for web and API testing.
Local AI-assisted pentest architecture: the efficiency layer that helps you test smarter, faster, and with less waste.

I can turn this next into a single downloadable markdown methodology pack, or into a side-by-side table showing where each workflow overlaps and where each adds something unique.