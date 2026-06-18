# operate-incident — worked example

A blameless incident record for a checkout outage.

> **Claude:** Payment success rate dropped to 12% — revenue-impacting, customer-facing → **sev1**. Paging on, status page to "investigating", 30-min comms cadence.
> Incident-command stood up: **commander** = Mira (decides, not debugging), **scribe** = Jon (timeline), **comms-lead** = Priya (status page), **SME** = Lee (hands-on). Runbook RB-07: failed over the payment gateway to the secondary region → success rate back to 99%. Stable. Root-cause hunt handed to the disciplined diagnosis loop.

Recorded — `10-operate/incident-2026-0142.md` (**blameless** — systems, not people):

| field | value |
|---|---|
| severity · roles | sev1 · commander Mira / scribe Jon / comms Priya / SME Lee |
| timeline | detected 14:02 · acknowledged 14:05 · mitigated 14:23 · recovered 14:31 |
| comms log | status-page 14:06 "investigating" · 14:31 "resolved" |
| impact | ~29 min degraded checkout, est. 1 850 failed payments |
| **error-budget consumed** | `SLO-checkout-availability` · **34%** (over 25% threshold → postmortem mandatory) |
| root cause | gateway connection pool exhausted under a retry storm (config, not a person) |
| action items | cap retries `OWNER Lee · JIRA-PAY-218 · open` · pool alert `OWNER Sam · JIRA-OPS-91 · done` |
| learnings → upstream | new `GAP`: no NFR bounding retry amplification → routed to discovery |

(timeline stamps → acknowledge 3 min / recovery 29 min as inputs to the upstream rollup; the new gap propagates to the spec, the postmortem isn't a dead document.)
