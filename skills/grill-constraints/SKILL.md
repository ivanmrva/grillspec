---
name: grill-constraints
description: >-
  Pin the fixed bounds the solution must live within — technical and organizational mandates,
  imposed standards, applicable regulatory regimes, the existing environment to reuse,
  stakeholders and sign-off authorities, and the assumptions the plan rests on. Loads the shared
  grill engine.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# grill-constraints

**Load `references/grill-engine.md` first and follow it.** This skill applies that method to **Constraints** — the fixed bounds the solution must live within.

## Rules
- a *preference* counts — record it as a **soft** constraint (vs **hard**) with its **source**, so the architecture derives without re-asking
- **testable or it isn't a constraint** — "must be fast" is a wish; "p95 < 200 ms, mandated by contract" is a constraint
- **every hard mandate names its downstream owner by id** — the artifact that operationalises it (`OBL-` for a regulatory bound · an `NFR-`/`ASR-` for a quality bound · a conventions fitness rule / `ADR-` for a stack, standard, or naming mandate) — mirroring how an `OBL-` carries its owner; a mandate row with no owner id is a bound the build will silently ignore, and the architecture/conventions derivations must be able to reach it by reference, not re-discover it in prose
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
- `references/grill-engine.md`
- Worked example: `examples.md`
