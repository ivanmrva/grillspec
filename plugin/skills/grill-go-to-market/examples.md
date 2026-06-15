# grill-go-to-market — worked example

Launching a self-serve API analytics tool, motion already set to product-led:
> **Claude:** Your ACV lands around $9k, but you've listed an outbound SDR team as the primary channel — at that ACV the CAC won't clear payback. I'd make **developer content + docs** primary and keep SDRs for expansion only. Who's the ICP — the developer or their VP?
> **User:** The developer adopts it; the VP approves the upgrade.

Recorded:
- `channels.md` — ICP: backend developer at a 20–200-eng SaaS company, champion = the dev, economic buyer = Eng VP. **Primary: developer content + docs SEO** (CAC ~$140, payback 2 mo, fits $9k ACV). **Secondary: open-source SDK** (CAC ~$90, payback 1.5 mo). **Tertiary: conference talks** (CAC ~$1.1k, payback 4 mo — flagged borderline at this ACV, capped at 15% of spend). SDR outbound dropped from primary: $6k blended CAC fails the ACV-band check.
- `launch.md` — **Soft** (trigger: 50 design-partner installs; channel: private Slack; gate: <2% error rate). **Limited** (trigger: NPS ≥ 30; channels: Show HN + newsletter; enablement: quickstart + 3 sample repos; gate: docs coverage 100%). **GA** (trigger: 500 WAU; channels: paid search + lifecycle email; gate: status page + on-call live).
- `partnerships.md` — Vercel (tech, marketplace listing → co-distribution, PLG-fit). Datadog (co-sell, shared dashboards → VP buyer reach, hybrid-fit). PostHog (channel, integration directory → top-of-funnel, PLG-fit).
- PQL → sales hand-off: account hits **3 active projects AND 1M tracked events in 14 days** → routed to AE for the VP upgrade conversation.

ADR: `adr/ADR-GTM-001.md` — demoted SDR outbound on ACV-band grounds.
