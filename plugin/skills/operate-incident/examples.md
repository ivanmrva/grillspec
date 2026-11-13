# operate-incident — worked example

Illustrative. A checkout outage on a small team.

**Triage and severity.** Payment success dropped to 12%: customers are affected and revenue is being lost now, so this is a live incident at the highest severity. Paging on, status page set to "investigating", an update to stakeholders every 30 minutes.

**Roles.** Mira decides and does not debug. Lee has hands on the system. Priya keeps the timeline and handles the status page.

**Stabilize.** The payment runbook says to fail the gateway over to the secondary region. After the failover, payment success returned to 99%. The cause is not yet known; the hunt was handed to `diagnose` once the system was stable.

Record — `12-operate/incident-2026-0142.md`:

| field | value |
|---|---|
| date · severity | 2026-04-17 · sev1 |
| roles | commander Mira · hands-on Lee · timeline and communications Priya |
| timeline | detected 14:02 · acknowledged 14:05 · mitigated 14:23 · recovered 14:31 |
| communications | status page 14:06 "investigating" · 14:31 "resolved" |
| impact | about 29 minutes of degraded checkout; an estimated 1 850 failed payments |
| error budget consumed | the checkout availability objective, SLO-003 · 34% (over the 25% threshold, so a postmortem is required) |
| root cause | the gateway connection pool was exhausted by a retry storm; nothing bounded retry amplification |
| action items | cap gateway retries · Lee · PAY-218 · open<br>alert on pool saturation · Sam · OPS-91 · done |
| spec and runbook changes | a quality target bounding retry amplification, added to the quality requirements; the failover runbook gained a pool-saturation check |

**Postmortem (blameless).** The retry policy was configured per client with no shared limit, so a slow gateway turned every client's retries into more load on the same pool. No single change caused it: the per-client defaults were each reasonable, and nothing in the spec asked for a bound across clients. The fix caps retries and adds a regression test that simulates a slow gateway; the missing quality target is now in the spec, so the next integration is designed against it.
