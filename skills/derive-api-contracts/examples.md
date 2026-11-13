# derive-api-contracts — worked example

Illustrative: it shows the shape, not required content.

Upstream: `UC-014` "place an order" (scope `SEC-012`, `orders:write`); published event `EVT-011` OrderPlaced; integration requirement: clients may retry safely.

## Decision mode (`standard`) — `index.md`

| Seam | Kind | Serves | Scope |
|---|---|---|---|
| API-007 Orders | REST | UC-014 | SEC-012 `orders:write` |
| EVT-011 OrderPlaced | event, `order.events` | UC-014 | internal consumers |

| Policy | Decision |
|---|---|
| Versioning | additive-only; a breaking change is a new version with a 90-day sunset (status: unconfirmed) |
| Errors | RFC 9457 `problem+json` |
| Idempotency | `Idempotency-Key` header required on every create |
| Event envelope | id · type · version · time · correlationId · source · data |
| Delivery | at-least-once, ordered per `orderId`, dead-letter queue per channel |

The shapes of `API-007` and `EVT-011` live in the contract package; consumer-driven contract tests check compatibility.

## Full mode (`regulated`) adds

`openapi.yaml` and `asyncapi.yaml` authored in the spec, each operation bound to the id graph:
```yaml
paths:
  /orders:
    post:
      operationId: placeOrder
      x-grillspec-id: API-007
      x-serves: [UC-014]
      security: [{ oauth2: [orders:write] }]
```
