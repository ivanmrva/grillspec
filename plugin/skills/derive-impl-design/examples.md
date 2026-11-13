# derive-impl-design — worked example

Illustrative. T-016, "Refund a payment", is `critical` (a money path), so its brief carries `design | design-first — 10-delivery/impl-design/T-016-refund-payment.md`. The note is written just before the slice is coded.

Given by the architecture and not re-decided here: the module's role, its dependency direction and its seam interface.

```
MOD-012 refund-service   role: application-service   depends inward (→ the Payment aggregate; out via driven ports)
refund(paymentId, amount, actor, idempotencyKey) -> Result<PaymentRefunded, RefundError>
```

## Output — `spec/10-delivery/impl-design/T-016-refund-payment.md`

```
implements MOD-012 · serves T-016

Mechanism
  1. look up the idempotency key; a known key returns the stored result (AC-016d)
  2. load the Payment; payment.requestRefund(amount, actor) applies the aggregate rules
  3. persist the Payment (refund pending), the idempotency record and an outbox entry in one transaction
  4. the outbox consumer calls the gateway's refund API with the same key; on success it settles
     the refund and publishes EVT-PaymentRefunded

The risk and its containment
  Money leaves once and cannot be recalled. The gateway call is the only irreversible step, so it
  runs outside the transaction, after the commit, and carries the idempotency key: a retry or a
  redelivered outbox entry cannot refund twice, and a failed call leaves a pending refund to retry.

Concurrency
  optimistic lock on Payment.version; one retry on a stale read; no long-held lock

Errors
  | error              | retryable | handling     | why                                             |
  | AmountExceedsPaid  | no        | propagated   | the caller must correct the amount              |
  | OverBranchLimit    | no        | propagated   | SEC-044 denial, shown to the actor              |
  | DuplicateRequest   | —         | designed-out | the key lookup returns the first result         |
  | GatewayUnavailable | yes       | masked       | the consumer retries; the refund stays pending  |
```

The note does not repeat the brief's criteria, shows no code, and adds no port beyond the gateway port the architecture already has. Calling the gateway from the outbox consumer is a costly-to-reverse choice a reader might not expect, so it is also recorded as `adr/ADR-IMPL-003.md` with the rejected alternative (call the gateway inside the command, then commit).
