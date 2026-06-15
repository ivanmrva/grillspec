---
name: grill-constraints
description: >-
  Pin the fixed bounds the solution must live within — technical & organizational mandates, externally-imposed standards & conventions, the regulatory regimes that apply, the existing environment to reuse, the stakeholders & sign-off authorities, and the assumptions & dependencies the plan rests on. Use when you need what limits design freedom nailed down before architecture. Loads the shared grill engine.
disable-model-invocation: true
argument-hint: an idea, existing docs, or a repo
---

# grill-constraints

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md` first and follow it.** This skill applies that method to **Constraints** — the fixed bounds the solution must live within.

## Rules
- a *preference* counts — record it as a **soft** constraint (vs **hard**) with its **source**, so the architecture derives without re-asking
- **testable or it isn't a constraint** — "must be fast" is a wish; "p95 < 200 ms, mandated by contract" is a constraint
- a standard/protocol the solution must implement (OAuth2/OIDC/SAML · FHIR · ISO 20022) is a **technical constraint**, not an integration detail
- **assumptions & dependencies are first-class** — surface them or they bite downstream
- **every gate/sign-off names a real accountable owner** (a person or role, not "the team") — so the release checklist has someone to ask

## Output
Written under `constraints/`:

| File | Captures | Format |
|---|---|---|
| `technical.md` | mandated/preferred stack · runtime · hosting · target env (OS/device · on-prem/cloud/air-gap · network) · standards/protocols to implement | constraint · hard/soft · source |
| `organizational.md` | budget · timeline · team size/skills/topology (who owns what) · mandated process & governance · contractual/licensing/IP | constraint · hard/soft · source |
| `stakeholders.md` | the (internal) stakeholder map + decision rights (responsible / accountable / consulted / informed per decision area) + the named **sign-off authorities** (legal · security · product · exec) — customer personas live in discovery | stakeholder · role · decision-rights · signs-off-for |
| `conventions.md` | externally-imposed doc-language · coding/naming/versioning standards — not the team's own (chosen later) | convention · source |
| `regulatory.md` | the regimes · certs · residency mandates that apply — the bounds only | regime · bound |
| `environment.md` | existing systems & the platform/tooling already run (cloud · CI · IdP · observability) — prefer over greenfield | system · owner · interface · commitment |
| `assumptions.md` | what the design takes as true (technical/operational) | assumption · owner · if-false→impact |
| `dependencies.md` | what the build waits on from outside (third-party systems · other teams · approvals · provisioning) | dependency · owner · needed-by |

ADRs → `adr/ADR-CON-NNN.md`

## Excludes
the chosen architecture (derived downstream) · the team's own coding conventions (chosen later — only *imposed* ones are constraints) · full regulatory obligations & retention values (→ compliance) · NFR targets (→ quality) · problem/market bets (→ discovery) · the external-actor / neighbor-system **boundary roster** (→ system context; existing systems appear here only as environment constraints)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/grill-engine.md`
- Worked example: `examples.md`
