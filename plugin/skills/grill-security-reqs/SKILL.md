---
name: grill-security-reqs
description: >-
  Build the threat model — assets, trust boundaries, threat actors, the authorization policy (actors × commands, default-deny), and audit/privacy obligations. Use when you need the threat model, not the mechanisms. Loads the shared grill engine.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-security-reqs

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **Security & privacy requirements** — the threat model, not the mechanism.

## Method
1. **Draw trust boundaries** from the context-map external seams + untrusted-input edges; list the assets that cross or sit on each.
2. **Security-threat enumeration** — walk a **per-element grid over the trust boundaries**: each element × the six categories (spoofing · tampering · repudiation · info-disclosure · denial-of-service · elevation-of-privilege) → for each plausible threat, a control or an accepted-risk.
3. **Privacy-threat pass** — walk the data-flows and personal-data assets against the seven privacy-threat categories (linkability · identifiability · non-repudiation · detectability · information disclosure · unawareness · non-compliance) → emit privacy threats with the **same id + owner discipline** as security threats.

## Rules
- **authorization is DEFAULT-DENY** — every command has an explicit who-may rule; an unspecified cell is forbidden, not allowed; carry ownership/tenant predicates in the condition cell (a user may act only on their own / their tenant's data)
- the **authorization model shape** (role- / attribute- / relationship-based + why) is recorded as an ADR — the ownership/tenant predicates already imply attribute/relationship-based
- every sensitive asset is in the threat model with **CIA emphasis** (sourced from the data classification + core-output integrity + audit trail + identities/secrets)
- threat actors named with **capability + motive** (external · malicious/negligent insider · domain-named adversary) **+ abuse/misuse cases per high-value asset**
- audit events identified with **append-only/tamper-evident + retention**; privacy obligations stated (lawful basis · data-subject rights incl. deletion)
- target a level of a **leveled application-security-verification standard** (OWASP ASVS — pick L1/L2/L3 to the asset sensitivity) and anchor to the **current OWASP Top-10 edition**

## Output
Written under `requirements/security/`:

| File | Captures | Format |
|---|---|---|
| `authorization.md` | authz matrix — rule SEC-NNN: actor × command → allow/deny/condition (DEFAULT-DENY) with ownership/tenant predicates; model shape (role/attribute/relationship-based) noted, decided in an ADR | — |
| `threat-model.md` | security threats from the per-element grid (spoofing · tampering · repudiation · info-disclosure · DoS · elevation) → control-or-accepted-risk · privacy threats (linkability · identifiability · non-repudiation · detectability · disclosure · unawareness · non-compliance) → control-or-accepted-risk · assets · trust boundaries · threat actors (capability + motive) · abuse/misuse cases per high-value asset; ASVS target + OWASP Top-10 edition anchored | list: **`THR-` id** · asset · threat · boundary · control/accepted-risk · owner |
| `privacy-audit.md` | privacy/compliance obligations (lawful basis · data-subject rights) + audit requirements (what's logged · append-only · retention); privacy threats may land here instead of `threat-model.md` | bullet lists |

ADRs → `adr/ADR-SREQ-NNN.md`
Consumes: the data classification (assets + retention rules to cross-reference), the domain context-map's external seams (trust boundaries), the domain commands (the rows of the authz matrix), and the go-to-market motion (sales-led → enterprise SSO/SCIM).

## Excludes
authn/authz *mechanisms*, encryption, secrets, IdP, and the implementation of the chosen authorization model (→ the architecture)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
