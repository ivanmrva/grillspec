---
name: grill-security-reqs
description: >-
  Set the security and privacy requirements: the authorization policy (who may run which command,
  default-deny), the product-specific threats with a control or accepted risk each, and the audit
  obligations. Use when you need the rules and the threat model, not the mechanisms.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-security-reqs

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **Security & privacy requirements** — the threat model, not the mechanism.

## Depth by profile
| Profile | What the interview captures |
|---|---|
| `lite` | not a separate area. |
| `standard` | `authorization.md` in full: every command's who-may rule, including the deny paths. In `threat-model.md`, the handful of threats specific to this product (its valuable assets, its trust boundaries, its abuse cases), each with a control or an accepted risk. Threats every web application shares are covered by the verification level and are not listed one by one. `privacy-audit.md` holds the audit requirements. |
| `regulated` | the exhaustive passes as well: the per-element grid over every trust boundary, and the privacy-threat pass over every personal-data flow. |

## Method
1. Draw the trust boundaries from the context map's external seams and the untrusted-input edges. List the assets that cross or sit on each.
2. Find the threats. At `standard`, ask for each high-value asset what an attacker or a careless insider would do with it. At `regulated`, walk every boundary element against the six security categories: spoofing · tampering · repudiation · information disclosure · denial of service · elevation of privilege.
3. At `regulated`, walk the data flows and personal-data assets against the seven privacy categories: linkability · identifiability · non-repudiation · detectability · information disclosure · unawareness · non-compliance. A privacy threat carries an id and an owner like any other threat.

Each plausible threat ends with a control or an accepted risk.

## Rules
- Authorization is default-deny. Every command has an explicit who-may rule, and an unspecified cell means forbidden. The condition cell carries the ownership or tenant predicate: a user acts only on their own, or their tenant's, data.
- Default-deny is yours to decide. Each allow rule and each accepted risk is the organisation's policy, so the user ratifies it. Mark a threat `accepted-risk` only once the user has accepted it; accepting risk on their behalf hides an exposure they never saw.
- State each rule so its deny case is unambiguous. The task that builds the rule exercises the deny path in a test, because enforcement that is never invoked on the deny branch proves nothing.
- The shape of the authorization model (role-, attribute- or relationship-based, and why) is recorded as an ADR. Ownership and tenant predicates already imply attribute- or relationship-based.
- Every sensitive asset is in the threat model with its confidentiality, integrity or availability emphasis. Assets come from the data classification, the integrity of the product's core output, the audit trail, and identities and secrets.
- Threat actors are named with capability and motive (external · malicious or negligent insider · a domain-specific adversary), with abuse cases for each high-value asset.
- Audit events are identified with their tamper-evidence (append-only) and retention. Each privacy obligation (lawful basis, data-subject rights including deletion) cites the `OBL-`, `SEC-` or `DATA-` id that owns it.
- The verification level is an OWASP ASVS level (L1 / L2 / L3) chosen to the asset sensitivity and anchored to the current OWASP Top 10. Where the quality area already carries the level as an `NFR-`, cite that id.

## Output
**IDs:** `SEC-` authorization rule · `THR-` threat (security or privacy).
Written under `requirements/security/`:

| File | Captures | Format |
|---|---|---|
| `authorization.md` | the authorization model, one rule per row, and the model shape with its ADR | table with the columns `SEC-id · actor · command · decision · condition` |
| `threat-model.md` | assets · trust boundaries · threat actors · abuse cases · the threats · the verification level | per threat: `THR-` id · asset · threat · boundary · control / accepted-risk · owner |
| `privacy-audit.md` | audit requirements (what is logged · append-only · retention) and privacy obligations; privacy threats may be listed here | `THR-` rows + `OBL-` / `SEC-` / `DATA-` refs |

In `authorization.md` the decision is allow or deny, the command cell holds the `CMD-` id, every command has at least one row, and no cell is blank.

Each threat's entry names its control by id (a `SEC-` rule, an ADR, an `OBL-`) or says `accepted-risk`; the coverage check reads the entry for one of them. A privacy threat keeps its `THR-` id whichever file it sits in.

ADRs → `adr/ADR-SREQ-NNN.md`
Consumes: the data classification (assets and retention rules to cross-reference), the external seams on the domain context map (trust boundaries), the domain commands (the rows of the authorization table), and the go-to-market motion (sales-led implies enterprise SSO/SCIM).

## Excludes
authn/authz *mechanisms*, encryption, secrets, IdP, and the implementation of the chosen authorization model (→ the architecture)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
