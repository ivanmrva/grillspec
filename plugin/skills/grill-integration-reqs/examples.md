# grill-integration-reqs — worked example

Illustrative: it shows the shape of the output, not a list to fill. A product on the `standard` profile; of its external seams only the payment provider moves money.

> **Agent:** When we send a capture and the provider times out, do we retry? If so we need an idempotency key, or we will double-charge. *(I'd make capture at-least-once and idempotent on the invoice id, with a 24 h dedup window.)*
> **User:** Yes, retry. We have double-charged before, so idempotency is mandatory.
> **Agent:** How do we catch a capture that silently went missing — a nightly reconciliation against their settlement report?
> **User:** Nightly, invoice id is the match key, and a drift opens a finance ticket.

## Output — `payment-provider.md`
elicits IF-004

- direction: outbound capture, inbound settlement
- interaction-style: sync request-reply (capture) · webhook push (settlement)
- what-flows: invoice capture request; settlement confirmation back
- volume: about 8k captures a day, peak 3× at month-end · quota: 50 req/s
- latency: capture < 2 s p95 · SLA: 99.9%
- delivery-guarantee: effectively-once
- idempotency: key = invoice id · dedup window 24 h
- retry/backoff: exponential, 5 attempts, then a finance review queue
- reconciliation: nightly · comparison key = invoice id · a gap opens a finance ticket
- owner: the provider's contract · auth: mTLS + API key

## Output — `seams.md`
| seam | elicits | direction | interaction-style | what-flows | on-failure |
|---|---|---|---|---|---|
| SMS gateway | IF-005 | outbound | async messaging | appointment reminders | drop after 3 tries |
