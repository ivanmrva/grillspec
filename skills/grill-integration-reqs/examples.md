# grill-integration-reqs — worked example

Specifying the seam to the *payment provider* that captures the card once a repair invoice is settled.

> **Claude:** When we send a capture and the provider times out, do we retry? If so we need an idempotency key, or we'll double-charge. *(I'd make capture at-least-once + idempotent on the invoice-id, with a 24h dedup window — never claim exactly-once.)*
> **User:** Yes, retry — and we've double-charged before, so idempotency is mandatory.
> **Claude:** And how do we catch a capture that silently went missing — a nightly reconciliation against their settlement report, keyed on invoice-id?
> **User:** Nightly recon, invoice-id is the match key; a drift opens a finance ticket.

Recorded: the payment seam with its delivery contract and reconciliation bar.

## Output
`requirements/integration/payment-provider.md`

**Payment provider seam**
- direction: outbound (us → provider) · interaction-style: sync request-reply (capture) + webhook push (settlement)
- what-flows: `Invoice` capture request; `SettlementConfirmed` event back
- volume: ~8k captures/day, peak 3× at month-end · backpressure: respect provider 50 req/s quota
- latency: capture <2s p95 · SLA: provider 99.9% availability
- delivery guarantee: **at-least-once + idempotent (effectively-once)**
- idempotency: key = invoice-id · dedup window = 24h
- ordering: none required (captures independent) · partition key = n/a
- retry/backoff: exponential, 5 attempts, then DLQ
- DLQ/poison: failed captures → finance review queue
- replay/backfill: re-drive DLQ after provider incident, idempotency prevents double-charge
- reconciliation: nightly · comparison key = invoice-id · gap → finance ticket
- owner: their API (contract = provider's) · auth: mTLS + API key
