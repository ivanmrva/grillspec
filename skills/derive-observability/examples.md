# derive-observability — worked example

Illustrative: it shows the shape, not required content.

Upstream: `NFR-007` "booking confirmation returns in ≤ 800 ms for 99% of requests" and `NFR-009` "the nightly export finishes by 06:00".

## Decision mode (`standard`) — `slos.md`

| id | maps-to | objective | SLI | error budget | on breach |
|---|---|---|---|---|---|
| SLO-001 | NFR-007 (booking latency) | 99% of `POST /bookings` complete in ≤ 800 ms over 30 days | good = latency ≤ 800 ms and status < 500, over valid requests | 1% ≈ 7h18m per 30 days | page |
| SLO-002 | NFR-009 (export deadline) | 29 of 30 nightly exports finish by 06:00 | export `completed_at` ≤ 06:00 | 1 late run per 30 days | ticket |

## Full mode (`regulated`) adds

`telemetry.md` — the event SLO-001 is computed from:
```
event=http.server.request route=/bookings http.response.status_code=201
  duration_ms=612 tenant.id=… booking.id=… trace_id=…
```

`alerting.md` — the SLO-001 alert: page when the budget burns faster than 14.4× over both 1h and 5m; ticket above 3× over both 6h and 30m. Each links SLO-001, the latency runbook and the booking dashboard.
