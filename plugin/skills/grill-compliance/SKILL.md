---
name: grill-compliance
description: >-
  Pin which regulatory and legal regimes apply and turn them into concrete, referenceable
  obligations (OBL-), each with the control that owns it. Swiss/EU-aware (FADP, GDPR, EU AI Act).
  Use when the product handles personal data, embeds AI, or sells into a regulated market.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-compliance

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **Compliance & regulatory obligations** — the regimes that apply and the obligations they force.

## Depth by profile
| Profile | What the interview captures |
|---|---|
| `lite` | not a separate area: the constraints carry the regulatory bounds. |
| `standard` | `regimes.md` (the regimes that apply, each with its trigger) and `obligations.md` (each obligation with the control that owns it). `ai-systems.md` when the product has an AI component. |
| `regulated`, or where a regime demands the document itself | `ropa.md`, `dpia.md` and `glossary.md` as well. At `standard` a processing register or an impact assessment is written only when an applicable regime requires that document to exist. |

## Rules
- The operating footprint is the user's to confirm: which jurisdictions and markets the product operates in, and who its customers are. Once the footprint is fixed, what each regime forces is derived on merit.
- Sweep the footprint for two kinds of regime. Statutory: data protection (FADP, GDPR, state and national privacy acts), the EU AI Act, accessibility law, sector rules. Contractual or certification, triggered by customer demand: ISO 27001, SOC 2, PCI-DSS. These names are prompts for the sweep. List a regime when it applies or is a real candidate, with its trigger; record N-A only where a reader would expect the regime to apply.
- Each obligation carries an `OBL-` id and a downstream owner (a `SEC-` rule · a `DATA-` class · UX · the architecture) or a recorded gap. The id is what a task brief cites, so an obligation without one never reaches the build.
- Each AI component is risk-tiered {prohibited · high-risk · limited · minimal} with its rationale. High-risk pulls the obligation checklist (risk management · data governance · logging/traceability · human oversight · transparency · conformity assessment); limited pulls the disclosure duty. Each pulled item is its own `OBL-` row in `obligations.md`, and `ai-systems.md` cites those ids.
- Two impact-assessment triggers fire independently: the data-protection one (personal-data processing) and the fundamental-rights one (an AI system that affects people's rights). Every finding that demands an action (a mitigation, a pseudonymisation, a residual risk someone must own) becomes an `OBL-`, or a `THR-` raised to security, with its owner. A finding left as prose is a legal duty nothing builds.
- Register rows cite the `DATA-` classes they cover. A retention or residency they restate matches the `DATA-` row, so the register cannot drift from the data requirements.
- Accessibility law produces an `OBL-` owned by UX, with the current WCAG at AA as its target.
- This area captures obligations, not legal advice. Flag what needs a lawyer, and state no more legal certainty than the sources support.

## Output
**IDs:** `OBL-` a concrete compliance obligation.
Written under `requirements/compliance/`:

| File | Captures | Format |
|---|---|---|
| `regimes.md` | the applicable and candidate regimes per jurisdiction | regime · jurisdiction · status (applies / candidate / N-A) · trigger |
| `obligations.md` | the concrete obligations: the rule and what it forces | `OBL-` id · rule · forces · owner |
| `ai-systems.md` | per AI component, its risk tier and the duties the tier pulls | component · tier · rationale · `OBL-` refs · fundamental-rights assessment triggered? |
| `ropa.md` | the processing register, one row per processing activity | activity · purpose · `DATA-` refs · recipients · transfers · retention |
| `dpia.md` | the outcome of each data-protection or fundamental-rights impact assessment | assessment · trigger-met · findings (`OBL-` / `THR-` refs) · residual-risk |
| `glossary.md` | the regulatory lexicon (controller · processor · data subject · …) | term · definition |

Obligations typically cover data-subject rights, the processing register, cross-border transfer mechanisms (adequacy, SCCs), consent and lawful basis, breach-notification timelines, accessibility, and impact-assessment triggers.

ADRs → `adr/ADR-COMP-NNN.md`
Consumes: the constraints — the regulatory, legal and jurisdictional mandates that fix which regimes apply.

## Excludes
the *implementation* of controls (→ the architecture) · legal advice (flag: needs counsel) · retention *values* (→ the data requirements; here only as the obligation)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
