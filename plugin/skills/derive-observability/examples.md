# derive-observability — worked example

From the NFR: *"booking confirmation returns in ≤ 800 ms for 99% of requests."* That recorded input drives the observability design below.

**SLO** (`slos.md`):

| id | objective | SLI | error budget |
|---|---|---|---|
| SLO-001 | 99% of `POST /bookings` complete in ≤ 800 ms over 30 days | good = (latency ≤ 800 ms ∧ status < 500) ÷ valid requests | 1% = ~7h18m / 30d |

**Telemetry** (`telemetry.md`) — one wide structured event per request, emitted over OTLP through the collector with semantic-convention names:
```
event=http.server.request route=/bookings http.response.status_code=201
  duration_ms=612 tenant.id=… booking.id=… trace_id=…
```
SLI is computed from this primitive (logs/metrics/traces are views over it); golden signals + resource method (utilization · saturation · errors) + service method (rate · errors · duration) instrumented.

**Alert** (`alerting.md`) — multi-window multi-burn-rate on SLO-001:
> **page** if burn-rate > 14.4× over 1h **AND** > 14.4× over 5m (fast: ~2% budget in 1h); **ticket** if > 3× over 6h **AND** > 3× over 30m (slow). Each links SLO-001 → the latency runbook → the booking dashboard. Error-budget policy: freeze releases on exhaustion.
