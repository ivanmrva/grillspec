---
name: derive-security-architecture
description: >-
  Design authn/authz mechanisms, encryption, secrets and identity from the security requirements. Use when the security requirements exist and you need authn/authz, encryption and secrets mechanisms designed. Loads the shared derive core.
disable-model-invocation: true
argument-hint: a recorded spec or design docs
---

# derive-security-architecture

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md` first and follow it.** This skill applies that method to **Security architecture** — authn/authz, encryption, secrets and identity.

## Method
1. threat model — enumerate threats as a **per-element grid over the data-flow's trust boundaries → mitigating control** (each crossing × threat category → control; abuse cases → security tests)
2. per authz rule + asset: the mechanism (enforcement point + ownership/tenant predicate)
3. encryption (at rest/in transit + key management) → secrets management
4. control mapping (OWASP Top-10 / ASVS level), extended to a national catalog (e.g. NIST CSF / 800-53) when the compliance area flags a jurisdiction

## Rules
- every trust-boundary crossing × threat category maps to a control; every authz rule realised with its **enforcement point + ownership predicate**
- a **zero-trust** posture is stated: per-request default-deny · least-privilege · assume-breach · no implicit trust in network location
- token design conforms to **OAuth + OIDC (current best practice)** (PKCE · authorization-code flow · no implicit or resource-owner-password grants)
- supply-chain targets a **build-provenance level (SLSA)** + signed-artifact attestation alongside SBOM/SCA
- session/secrets/supply-chain/anti-automation/tenancy all addressed
- controls mapped to OWASP/ASVS

## Output
Written under `solution/security/`:

| File | Captures | Format |
|---|---|---|
| `controls.md` | threat grid (trust-boundary crossing × category → control) + zero-trust posture (per-request default-deny · least-privilege · assume-breach · no network-location trust) — per control: mechanism · maps-to(SEC-) (abuse cases → security tests) | grid + per control: mechanism · maps-to(SEC-) |
| `authn-authz.md` | authn + identity/IdP; authorization model (RBAC/ABAC + enforcement points + ownership/tenant predicate); token design conforming to **OAuth + OIDC (current best practice)** (PKCE · authorization-code · no implicit/password grants · lifetime · refresh · revocation · storage · CSRF) | prose |
| `crypto-secrets.md` | encryption at rest/in transit + key management (KMS/rotation/envelope); secrets management (vault · rotation · no-secrets-in-code) | typed fields |
| `supply-chain.md` | supply-chain — **build-provenance level (SLSA)** + signed-artifact attestation · SCA · SBOM · pinned deps · anti-automation (lockout/rate-limit) · multi-tenancy isolation · control mappings (OWASP Top-10 / ASVS, + national catalog e.g. NIST CSF/800-53 when jurisdiction flagged) | prose |

ADRs → `adr/ADR-SEC-NNN.md`
*(DERIVED & regenerate-only — never hand-edited)*
Consumes: the security requirements (`SEC-` rules + trust boundaries + authz matrix) + the data-flow/architecture they sit on.

## Excludes
implementation code

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md`
- Worked example: `examples.md`
