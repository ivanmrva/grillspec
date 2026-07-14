# derive-security-architecture — worked example

**Upstream (settled):** `SEC-004` "a customer may read only their own orders"; trust boundary: browser → API gateway → Ordering service; assets: order PII + session token.

Threat grid — each boundary crossing × category → control (`controls.md`):

| Crossing | Threat category | Control | maps-to |
|---|---|---|---|
| browser → gateway | Spoofing | OAuth bearer (JWT) validated at gateway; mTLS gateway→service | SEC-001 |
| gateway → Ordering | Elevation of privilege | Ownership predicate: `order.customer_id == token.sub`, default-deny | SEC-004 |
| browser → gateway | Tampering | Per-request signature check; abuse case "alter order_id in URL" → security test | SEC-004 |

Zero-trust posture is stated: every request re-authenticated, least-privilege scopes, assume-breach (no implicit trust from being inside the VPC).

Token design (`authn-authz.md`): **OAuth + OIDC**, authorization-code flow with **PKCE** (no implicit, no resource-owner-password grants); access token 10 min, refresh token rotating with reuse-detection; stored in `HttpOnly; Secure; SameSite=Strict` cookie; CSRF via double-submit token.

Enforcement point for `SEC-004`: in the Ordering service repository layer, not the controller — the tenant/ownership predicate is applied to every query so a missing check fails closed.

Supply chain (`supply-chain.md`): target **SLSA Build Level 3** + signed-artifact attestation (cosign), SBOM (CycloneDX) on every build, pinned deps by digest; controls mapped to **OWASP ASVS L2**.

Recorded: the threat grid realising `SEC-004`/`SEC-001`, the OAuth+PKCE token design, the repository-layer ownership predicate, the SLSA-3 supply-chain target.
