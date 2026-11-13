# derive-test-strategy — worked example

Illustrative: it shows the shape, not required content.

Upstream: an integration-heavy booking service (three services and a queue); `API-002` `POST /bookings`; `NFR-007` "confirmation p99 ≤ 800 ms"; a `staging` environment.

## Decision mode (`standard`) — `levels.md`

Shape: integration-weighted — the behaviour lives in the queue and worker paths — with a thin e2e top. The e2e target is `staging`.

| tier | scope | real-deps | may-mock | mock-ceiling | target-env | coverage-bar | mutation-bar |
|---|---|---|---|---|---|---|---|
| unit | pure domain logic | — | — | none | local | 90% branch | 70% on changed domain |
| integration | a service with its store and queue | database, queue | payment provider | boundary-only | local | counted with unit | — |
| contract | `API-002`, consumer-driven | all | — | none | local | — | — |
| e2e | booking journey, smoke | all | — | none | staging | — | — |

Both bars are ratify-points (status: unconfirmed). The async confirmation is tested on the real queue and worker, asserting the eventual `confirmed` state.

## Full mode (`regulated`) adds

A row in `nfr-evidence.md`:

| requirement | evidence test | target |
|---|---|---|
| NFR-007 | load test, `POST /bookings` at 200 rps for 10 min | p99 ≤ 800 ms |
