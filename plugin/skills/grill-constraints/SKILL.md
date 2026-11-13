---
name: grill-constraints
description: >-
  Pin the fixed bounds the solution must live within: stack mandates and preferences, budget,
  timeline and team, residency and regulatory bounds, and the systems already in place. Use before
  the domain is modelled or the architecture is derived.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-constraints

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **Constraints** — the fixed bounds the solution must live within.

## Depth by profile
| Profile | What the interview captures |
|---|---|
| every profile | the one-way doors: stack mandates and preferences (`technical.md`), budget · timeline · team (`organizational.md`), residency and regulatory bounds (`regulatory.md`), and the systems already in place (`environment.md`). |
| `lite` | `environment.md` also lists every external system the product talks to and what crosses each boundary, because system context is not a separate area at `lite`. These are plain rows; interface ids belong to the system-context area. |
| when the project has them (expected at `regulated`) | `stakeholders.md`, `conventions.md`, `assumptions.md`, `dependencies.md`. A solo project with no sign-off authority, imposed standard or outside dependency writes none of them. |

## Rules
- A preference counts. Record it as a `soft` constraint (a mandate is `hard`) with its source, so the architecture can be derived without asking again.
- A constraint is testable. "Must be fast" is a wish; "p95 < 200 ms, mandated by contract" is a constraint.
- Every hard mandate names the area that carries it downstream: compliance for a regulatory bound, quality for a quality bound, the architecture or conventions for a stack, standard or naming mandate. A mandate with no owner is a bound the build never sees. Name the area in words in the `carried-by` cell, or cite the ADR that records it; this area sits upstream of the others, so it does not cite their ids.
- A standard or protocol the solution must implement (OAuth2/OIDC/SAML · FHIR · ISO 20022) is a technical constraint, not an integration detail.
- Surface assumptions and outside dependencies where they exist; an unstated one resurfaces as a blocked task.
- Every gate or sign-off names an accountable person or role, so the release has someone to ask. "The team" is not an owner.

## Output
Written under `constraints/`:

| File | Captures | Format |
|---|---|---|
| `technical.md` | mandated and preferred stack · runtime · hosting · target environment (OS/device · on-prem/cloud/air-gap · network) · standards and protocols to implement | constraint · hard/soft · source · carried-by |
| `organizational.md` | budget · timeline · team size, skills and ownership · mandated process and governance · contractual, licensing and IP bounds | constraint · hard/soft · source |
| `regulatory.md` | the regimes, certifications and residency mandates that apply — the bounds only | regime · bound |
| `environment.md` | existing systems and the platform already run (cloud · CI · IdP · observability); reuse is preferred over greenfield | system · owner · interface · commitment |
| `stakeholders.md` | the internal stakeholder map, decision rights per decision area, and the named sign-off authorities (legal · security · product · exec) | stakeholder · role · decision-rights · signs-off-for |
| `conventions.md` | externally imposed documentation language and coding, naming or versioning standards | convention · source |
| `assumptions.md` | what the design takes as true (technical / operational) | assumption · owner · if-false → impact |
| `dependencies.md` | what the build waits on from outside: third-party systems · other teams · approvals · provisioning | dependency · owner · needed-by |

ADRs → `adr/ADR-CON-NNN.md`

## Excludes
the chosen architecture (derived downstream) · the team's own coding conventions (chosen later; only imposed ones are constraints) · full regulatory obligations & retention values (→ compliance) · NFR targets (→ quality) · problem/market bets (→ discovery) · customer personas (→ discovery) · the external-actor and neighbor-system boundary roster with its interface ids (→ system context; existing systems appear here as environment constraints)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
