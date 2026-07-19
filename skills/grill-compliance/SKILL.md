---
name: grill-compliance
description: >-
  Pin which regulatory/legal regimes apply and turn them into concrete, referenceable obligations (`OBL-`) that flow into security, data, and architecture. Swiss/EU-aware (FADP/GDPR/EU AI Act). Use when you need the applicable regimes and their obligations nailed down. Loads the shared grill engine.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# grill-compliance

**Load `references/grill-engine.md` first and follow it.** This skill applies that method to **Compliance & regulatory obligations** — the regimes that apply and the obligations they force.

## Rules
- each obligation carries an **`OBL-`** id + a downstream owner (`SEC-` / `DATA-` / UX / arch) or a logged gap — and at build time an `OBL-` binds the implementing slice through its **`security` dimension**, so the Verification Record carries it as an evidenced obligation row, never just a spec-level note
- **jurisdiction sweep names every candidate regime** — statutory (FADP · GDPR · EU AI Act · accessibility law: EAA (in force) + ADA · US-state-privacy + India DPDP as candidates · sector rules) **and** contractual/certification regimes (ISO 27001:2022 · SOC 2 · PCI-DSS), the latter triggered by customer/market demand — each marked applies/candidate/N-A with its trigger
- **the operating footprint is the user's to confirm; the obligations are then derived** — *which* jurisdictions/markets you operate in and who your customers are are facts the user/org holds (confirm/ratify, don't presume); once the footprint is fixed, *what each regime forces* is derived on merit
- **each AI component is risk-tiered** {prohibited · high-risk · limited · minimal} with rationale; high-risk pulls the obligation checklist (risk-management · data-governance · logging/traceability · human-oversight · transparency · conformity-assessment), limited pulls the disclosure duty — **each pulled checklist item is minted as its own `OBL-` row in `obligations.md`** (the checklist in `ai-systems.md` cites those ids; an inline prose checklist item no `OBL-` carries is unreachable by every downstream gate)
- **two distinct impact-assessment triggers** — the data-protection one (personal-data processing) and the **fundamental-rights** one (an AI system affecting people's rights) — fire independently; each assessment's outcome is itself an artifact, and **every DPIA finding that demands an action (a mitigation, a pseudonymisation, a residual risk someone must own) lands as an `OBL-` (or a `THR-` raised to security) with its downstream owner** — a finding that stays prose inside `dpia.md` is a legally-mandated action nothing will ever build
- **RoPA rows cite the `DATA-` classes they register** — the retention/residency stated per activity then falls under the typed-scalar agreement check (a value restated must match the `DATA-` row), so the register can't silently drift from the data requirements
- accessibility law emits an `OBL-` owned to **UX** (target = current WCAG at AA)
- this captures **obligations, not legal advice** — flag anything that needs a lawyer; don't invent legal certainty

## Output
**Stable IDs** (bare type prefix, ID = the leading table column / row key): `OBL-` a concrete compliance obligation.
Written under `requirements/compliance/`:

| File | Captures | Format |
|---|---|---|
| `regimes.md` | applicable + candidate regimes per jurisdiction: statutory (FADP · GDPR · EU AI Act · EAA/ADA accessibility · US-state-privacy · India DPDP · sector) + contractual/certification (ISO 27001:2022 · SOC 2 · PCI-DSS, trigger = customer/market demand) | regime · jurisdiction · status · trigger |
| `obligations.md` | concrete obligations — id OBL-NNN: the rule + what it forces (data-subject rights · processing register (RoPA) · cross-border transfer mechanisms (adequacy/SCCs) · consent/lawful-basis · breach-notification timelines · accessibility (current WCAG at AA) · impact-assessment triggers) | OBL-id · rule · forces · owner |
| `ai-systems.md` | per AI component: risk-tier {prohibited · high-risk · limited · minimal} · rationale · high-risk → obligation checklist **as `OBL-` citations** (each item minted in `obligations.md`, cited here by id) · limited → disclosure duty (`OBL-`) · fundamental-rights-impact-assessment trigger | component · tier · rationale · `OBL-` refs |
| `ropa.md` | processing register, one row per processing activity: purpose · **`DATA-` classes registered** · recipients · transfers · retention (must agree with the cited `DATA-` rows) | activity · purpose · `DATA-` refs · recipients · transfers · retention |
| `dpia.md` | data-protection / fundamental-rights impact-assessment outcomes (the assessment result, not the trigger) — every action-demanding finding minted as an `OBL-`/`THR-` with owner, cited here by id — or an ADR where load-bearing | assessment · trigger-met · findings (`OBL-`/`THR-` refs) · residual-risk |
| `glossary.md` | regulatory lexicon (controller · processor · data-subject · …) | term · definition |

ADRs → `adr/ADR-COMP-NNN.md`
Consumes: the **constraints** — the regulatory/legal/jurisdictional mandates that fix which regimes apply (turned here into concrete `OBL-` obligations).

## Excludes
the *implementation* of controls (→ the architecture) · legal advice (flag: needs counsel) · retention *values* (→ the data requirements; here only as the obligation)

## Resources
- `references/grill-engine.md`
- Worked example: `examples.md`
