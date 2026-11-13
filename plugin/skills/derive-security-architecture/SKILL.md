---
name: derive-security-architecture
description: >-
  Decide the security mechanisms — identity provider, authorization model and enforcement points, session and token design, key management and secrets — and at the regulated profile also the control register and supply chain. Use when the security requirements exist.
disable-model-invocation: true
argument-hint: a recorded spec or design docs
---

# derive-security-architecture

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md` first and follow it.** This skill applies that method to the **security architecture**: authentication, authorization, encryption, secrets and identity.

## Depth by profile
How much is written follows the project's profile:

| Profile | Mode | Written |
|---|---|---|
| `lite` | N/A | nothing here — the sign-in and key-management choices are rows in `arch/solution-strategy.md`, the rest is in the conventions |
| `standard` | decision mode | `authn-authz.md`, `crypto-secrets.md` |
| `regulated` | full mode | those two plus `controls.md`, `supply-chain.md` |

Decisions live in the spec; the description lives in the artifact that enforces it — here the authorization policy in code and the deny-path tests that exercise it — and once code exists they are the source of truth for the rule-by-rule control register. Decision mode therefore records only who authenticates users, where each authorization rule is enforced, how sessions and tokens work, and how keys and secrets are held; full mode also writes the register, because at `regulated` it is a deliverable auditors read.

## Decision record
`authn-authz.md`:
- the identity provider — a vendor one-way door, so a ratify-point: propose a provider with a one-line reason and surface it as the engine describes;
- the authorization model (RBAC/ABAC) and, for every `SEC-` authorization rule, its enforcement point and its ownership or tenant predicate. Authorization is default-deny: a request no rule allows is refused at the enforcement point;
- session and token design — lifetime · refresh · revocation · storage · CSRF — and the limits on sign-in abuse (lockout, rate limit). Where the product uses OAuth or OIDC it follows current best practice: authorization-code flow with PKCE, no implicit or resource-owner-password grant.

`crypto-secrets.md`:
- encryption at rest and in transit, with key management (KMS · rotation · envelope encryption);
- secrets handling — where secrets are stored, how they rotate, and that none lives in code or the repository.

## Output
Written under `solution/security/`. The rows marked `full` are written only at `regulated`; in decision mode their content is not raised.

| File | Mode | Captures | Format |
|---|---|---|---|
| `authn-authz.md` | decision | the decision record above | enforcement table keyed on `SEC-`: rule · enforcement point · predicate; short prose for the rest |
| `crypto-secrets.md` | decision | the decision record above | typed fields |
| `controls.md` | full | the threat grid: each trust-boundary crossing of the data flow × threat category → the mitigating control (an abuse case becomes a security test) · the zero-trust posture: per-request default-deny, least privilege, assume-breach, no trust from network location | grid, then per control: mechanism · maps-to (`SEC-`) |
| `supply-chain.md` | full | SBOM and dependency scanning · pinned dependencies · the build-provenance level (SLSA) with signed-artifact attestation · anti-automation · multi-tenancy isolation · control mappings (OWASP Top-10 and an ASVS level; a national catalog such as NIST CSF or 800-53 when the compliance area flags a jurisdiction) | short sections |

ADRs → `adr/ADR-SEC-NNN.md`
Consumes: the security requirements (`SEC-` rules, trust boundaries, the authorization matrix) and the data flow and architecture they sit on.

## Excludes
implementation code · in decision mode, the per-rule control register (the authorization policy and its deny-path tests state it)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md`
- Worked example: `examples.md`
