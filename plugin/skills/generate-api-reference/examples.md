# generate-api-reference — worked example

Projecting one `API-` contract into a consumer-facing reference entry, with a sunset note.

> **Claude:** Rendered from the contract for `API-CreateBooking` (no OpenAPI artifact present, so generated from the contract definition); grouped under the **Bookings** resource, cross-linked to `API-CreateBooking` / `DATA-Booking`.

`docs-site/api/bookings.html` — entry:

- **POST `/v1/bookings`** — Create a repair booking
- **Auth:** Bearer (OAuth2) · scope `bookings:write` (→ `SEC-Booking`)
- **Request** (`DATA-Booking`): `{ branchId: string, slot: ISO-8601, customerId: string }`
- **Responses:** `201` → `{ id, status: "pending" }` · `409` slot taken · `422` validation
- **Example:**
  `curl -X POST /v1/bookings -H "Authorization: Bearer $T" -d '{"branchId":"BR-7","slot":"2026-07-01T09:00Z","customerId":"C-88"}'`
- **Try-it:** request/response playground (static-only fallback: importable HTTPie/Postman snippet)

- **GET `/v1/bookings/{id}`** — Fetch a booking
- **Auth:** Bearer (OAuth2) · scope `bookings:read` (→ `SEC-Booking`)
- **Responses:** `200` → `DATA-Booking` · `404` not found · `403` not your branch

*(both endpoints render under one **Bookings** resource group — the reference groups by resource, not one file per route.)*

**Deprecation / sunset note** (mirrors the `Deprecation` + `Sunset` HTTP headers):
> `customerName` (string) is **deprecated** — replaced by `customerId`. `Deprecation: true` · **`Sunset: 2026-09-30`** · replacement → `DATA-Customer.id`. After the sunset date the field is dropped; clients must send `customerId`.

This also lands on `changelog.html` (changelog + all deprecations/sunsets). Each status maps to remediation in the shared `errors.html` catalog:

| code | meaning | remediation (RFC 9457 `problem+json`) |
|---|---|---|
| 409 | slot already taken | re-fetch availability, choose another slot |
| 422 | validation failed | fix the field named in `problem.detail` |
| 403 | wrong branch | use a token scoped to the booking's branch |

(regenerated wholesale — pure projection of the contracts, no spec edits; embedded as the doc-site's API section, or standalone under `docs-site/api/`.)
