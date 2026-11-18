# AI use on the Orion engagement

AI tools are allowed on this engagement. Every use is logged, and how well you review what comes back is assessed.
Treat `data/source/`, `orion.db` and everything derived from them as **client production data**.

| Allowed in the programme-approved AI tool | Never, in any tool |
|---|---|
| Kit code, BRD, STTM, handbook and your own tests | Anything from `data/source/` or `orion.db`, including evidence files |
| Logs after redaction with `qa_lib/redact.py` | Unredacted logs |
| Schema, table and column names | Public AI tools, or any tool on a personal device |

Customer names, emails and birth dates are **Restricted** (handbook S11). They never leave the kit, and they never
belong in evidence files: keep the keys, drop or mask the Restricted columns.

## Before you paste anything: STOP / CHECK FIRST / GO

*Draft from the kit. If the 2 Nov guardrails one-pager differs, the one-pager wins.*

**STOP** if the text contains client data (rows, names, emails, birth dates, amounts tied to a customer),
credentials, hostnames or IP addresses, or if the tool is not the programme-approved one.

**CHECK FIRST** if you are unsure whether something counts as client data, if a log or error message might carry
identifiers, or if you plan to paste more than a short code excerpt. Redact with `qa_lib/redact.py`, then ask your
test lead.

**GO** for kit code, requirements, your own test code, schema names and redacted text, in the approved tool.

## Logging

Record every use in `templates/07_ai_usage_log.md`: what you asked, what came back, what you kept, and why.
A use that isn't logged counts as a use that wasn't reviewed.
