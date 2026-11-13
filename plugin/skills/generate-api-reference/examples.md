# generate-api-reference — worked example

Illustrative. One resource page, built from the contract package in the code (this project keeps its OpenAPI there) with IDs from the seam index.

## `docs-site/api/bookings.html`

Both endpoints sit under one Bookings group: the reference groups by resource, not one file per route.

**POST `/v1/bookings`** — Create a repair booking (`API-CreateBooking`)

- Auth: Bearer (OAuth 2) · scope `bookings:write` (`SEC-Booking`)
- Request (`DATA-Booking`): `{ branchId: string, slot: ISO-8601, customerId: string }`
- Responses: `201` → `{ id, status: "pending" }` · `409` slot taken · `422` validation failed
- Example: `curl -X POST /v1/bookings -H "Authorization: Bearer $T" -d '{"branchId":"BR-7","slot":"2026-07-01T09:00Z","customerId":"C-88"}'`
- Try it: a request/response playground

**GET `/v1/bookings/{id}`** — Fetch a booking (`API-GetBooking`)

- Auth: Bearer (OAuth 2) · scope `bookings:read` (`SEC-Booking`)
- Responses: `200` → `DATA-Booking` · `403` not your branch · `404` not found

**Deprecation**, shown on the POST entry and collected on `changelog.html`:

> `customerName` is deprecated; send `customerId` instead. `Deprecation: true` · `Sunset: 2026-09-30`. After the sunset date the field is ignored.

## `docs-site/api/errors.html`

| Code | Meaning | What the client should do |
|---|---|---|
| 403 | the token is not scoped to the booking's branch | use a token for that branch |
| 409 | the slot is already taken | fetch availability again and choose another slot |
| 422 | validation failed | correct the field named in the problem detail (RFC 9457 `problem+json`) |
