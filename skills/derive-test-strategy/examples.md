# derive-test-strategy — worked example

From the spec: an **integration-heavy** booking service (3 microservices + SQS), `ASR-004` "no inbound dependency from domain → infrastructure", `API-002` `POST /bookings`, and `NFR-007` "≤ 800 ms p99 confirmation." That recorded input drives the Tier-B strategy below.

**Test-distribution choice** (`levels.md`):
> architecture is integration-heavy → **integration-weighted** shape (the middle tier carries the weight: real broker/worker paths), not a unit pyramid; thin e2e top; avoid an e2e-top-heavy distribution. Contract tests are **CDC** with provider verification.

**Contract test** (`levels.md`, from `API-002`):
> CDC pact: consumer (web) ⨯ provider (Booking API) on `POST /bookings` → 201 + `Location` header + `booking.id` shape; provider-verification job replays the pact in CI. The async confirmation gets a real-path integration test (real SQS + worker, assert the eventual `confirmed` outcome, cover retry/idempotency/dead-letter — never assert mere enqueue).

**NFR-evidence row** (`nfr-evidence.md`):

| requirement | evidence test | target it measures against |
|---|---|---|
| NFR-007 | load test ⨯ `POST /bookings` at 200 rps for 10 min | p99 ≤ 800 ms (ties to SLO-001); fail the gate above it |

Authored early from the target, executed once a deployable system exists; shift-right adds canary verification tied to the burn-rate. `ASR-004` gets a dependency-direction fitness function (failing until the structure exists).
