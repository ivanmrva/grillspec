# conformance-review — worked example

Illustrative. T-016, "Refund a payment", is `critical` (a money path), so it needs this review before it can be done. Scope `changed`, run by a subagent that did not write the code. The orchestrator withheld one criterion, AC-016d, from the implementer.

## Round 1

```
VERDICT: FAIL — a context boundary is crossed, and one deny path has no test.
```

The slice works and its suite is green, but two things diverge from the spec.

| Severity | Where | What diverges | Spec |
|---|---|---|---|
| blocking | `billing/app/refund-service.ts:41` | Imports `ledger/internal/LedgerRepository` and writes the reversal row itself. Billing may reach Ledger only through `EVT-PaymentRefunded`; the service's declared role is application-service, which depends inward only. | the context map; MOD-012 |
| blocking | `tests/` | SEC-044 (only a branch manager may refund above the branch limit) has no test that invokes the denial. The check exists in code; nothing exercises it. | SEC-044 |
| nit | `billing/domain/refund.ts:18` | `amt` where the glossary term is `refundAmount`. | glossary |

E2e not-exercised list:

| Criterion | Why the e2e leaves it out |
|---|---|
| AC-016c partial refund rounding | covered at unit level, as the tier contract allows for pure rules |
| AC-016b gateway timeout | covered by the integration test against the gateway container |

Held-out criterion: AC-016d (a second refund request with the same idempotency key returns the first result) — a fresh acceptance test tagged `@covers AC-016d` passes.

Checks run: the five tripwire scripts (clean), `check_contracts.py` (clean), `check_task.py spec --trace`. No UI in this slice, so nothing was rendered.

## Round 2

The implementer removed the import — the service emits `EVT-PaymentRefunded` and Ledger consumes it — and added the over-limit denial test.

```
VERDICT: PASS
```

The brief's `review` row is set to `PASS`.

## Lens B (advisory)

The refund-eligibility check is a shallow module: its interface is as complex as its one-line implementation. It is a candidate to fold into the `Refund` aggregate. Not urgent; it does not affect the verdict.
