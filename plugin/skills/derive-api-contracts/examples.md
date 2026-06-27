# derive-api-contracts — worked example

**Upstream (settled):** `API-007` "place an order" (scope `orders:write`); published event `EVT-011` OrderPlaced; integration req: clients may retry safely.

Contract authored **into the spec**, not prose. `openapi.yaml` slice:
```yaml
paths:
  /orders:
    post:
      operationId: placeOrder          # API-007
      x-serves: [UC-014]               # the use-case this endpoint fulfils — no orphan endpoint
      security: [{ oauth2: [orders:write] }]
      parameters:
        - { name: Idempotency-Key, in: header, required: true, schema: { type: string, format: uuid } }
      responses:
        '201': { description: Created, content: { application/json: { schema: { $ref: '#/components/schemas/Order' } } } }
        '409':
          description: Conflict
          content:
            application/problem+json:        # RFC 9457
              schema: { $ref: '#/components/schemas/Problem' }
              example: { type: "https://errors.acme.dev/order-already-placed", title: "Order already placed", status: 409 }
```

`asyncapi.yaml` channel slice (`EVT-011`):
```yaml
channels:
  order.events:
    address: order.events
    messages:
      orderPlaced:
        payload:
          type: object
          required: [id, type, version, time, correlationId, source, data]   # envelope
          properties:
            id: { type: string, format: uuid }
            type: { const: "com.acme.order.placed.v1" }
            version: { const: 1 }
            correlationId: { type: string, format: uuid }
        # delivery: at-least-once · ordering: per orderId key · DLQ: order.events.dlq
```

Versioning (`index.md`): additive-only; breaking change = new `type` suffix (`.v2`) + 90-day sunset header; consumer-driven contract tests gate CI.

Recorded: `API-007` with RFC 9457 `problem+json` + idempotency key + `orders:write` scope; `EVT-011` with full envelope, per-key ordering, DLQ; the versioning policy.
