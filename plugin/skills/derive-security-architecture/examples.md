# derive-security-architecture — worked example

Illustrative: it shows the shape, not required content.

Upstream: `SEC-004` "a customer may read only their own orders"; trust boundary browser → API gateway → Ordering service; assets: order PII and the session token.

## Decision mode (`standard`)

`authn-authz.md`:

| Rule | Enforcement point | Predicate |
|---|---|---|
| SEC-004 | Ordering repository layer, applied to every query | `order.customer_id == token.sub`; no match → denied |

The rule is enforced in the repository, not the controller, so a missing check fails closed.

- Identity provider: Auth0 (status: unconfirmed) — managed OIDC, so no in-house credential store to protect.
- Tokens: authorization-code flow with PKCE; access token 10 min; rotating refresh token with reuse detection; `HttpOnly; Secure; SameSite=Strict` cookie; CSRF by double-submit token.

`crypto-secrets.md`:
- at rest: provider-managed disk encryption, envelope keys in the cloud KMS, yearly rotation
- in transit: TLS everywhere, mTLS gateway → service
- secrets: platform secret store, injected at runtime, rotated on a staff change

## Full mode (`regulated`) adds

A threat-grid row in `controls.md`:

| Crossing | Threat category | Control | maps-to |
|---|---|---|---|
| browser → gateway | Tampering | abuse case "alter `order_id` in the URL" → security test | SEC-004 |

`supply-chain.md` then states the build-provenance target, SBOM generation and the ASVS level the controls map to.
