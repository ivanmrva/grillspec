# grill-go-to-market — worked example

Illustrative: it shows the shape of the output, not a list to fill. A self-serve API analytics tool with a product-led motion; the user is planning launch spend.

> **Agent:** Your ACV lands around $9k, but you list an outbound SDR team as the primary channel. At that ACV the acquisition cost will not pay back. I'd make developer content and docs primary and keep SDRs for expansion. Who is the ideal customer — the developer or their VP?
> **User:** The developer adopts it; the VP approves the upgrade.

## Output — `channels.md`
Ideal customer: a backend developer at a 20–200-engineer SaaS company; the engineering VP is the economic buyer.

| channel | message | expected CAC | payback | ACV-band fit |
|---|---|---|---|---|
| developer content + docs SEO (primary) | "see every API call in five minutes" | ~$140 | 2 months | fits |
| conference talks | case studies | ~$1.1k | 4 months | borderline; capped at 15% of spend |

SDR outbound is not a channel: a blended CAC of about $6k fails the check against a $9k ACV (ADR-GTM-001).

## Output — `launch.md`
| tier | trigger | channels | readiness gate |
|---|---|---|---|
| soft | 50 design-partner installs | private Slack | error rate < 2% |
| limited | NPS ≥ 30 | Show HN + newsletter | docs cover every endpoint |
| GA | 500 weekly active users | paid search + lifecycle email | status page and on-call live |

PQL → sales hand-off: an account with 3 active projects and 1M tracked events in 14 days is routed to sales.

No partners yet, so `partnerships.md` was not written.
