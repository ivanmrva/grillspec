# grill-problem-validation — worked example

Pinning the problem behind a tool that reconciles Stripe payouts against accounting ledgers for Shopify sellers.

> **Claude:** Who feels this most, and how often — is it the bookkeeper closing the month, or the founder spot-checking? *(I'd bet it's the bookkeeper, monthly, and it's a painkiller — a wrong close means a restated tax filing, not just annoyance.)*
> **User:** The bookkeeper, every month-end. Today they export both CSVs and match by hand in Excel — takes a full day and still misses fees.
> **Claude:** So the catalyst is the close deadline. What pulls them to a new way strongly enough to beat the habit of "Excel already works"?
> **User:** Audit season — one mismatched payout last year cost a client a $4k penalty.

Recorded:
- `problem.md` — who: SMB bookkeeper · frequency × intensity: monthly × high (painkiller) · current alternative: manual Excel CSV match (~1 day, misses processor fees) · why-now: audit-season penalty exposure · forces: push=$4k penalty + day lost / pull=auto-match / anxiety=trusting automation on tax data / habit="Excel works"
- `opportunities.md` — OPP-1 unreconciled Stripe fees (evidence: client $4k penalty · reach: ~all sellers · severity: high); OPP-2 multi-currency payout drift (reach: cross-border subset · severity: med)
- `bets.md` — BET-D1 bookkeepers will trust auto-categorized matches (desirability · criticality 5 · uncertainty 4 · status: unvalidated); BET-F1 Stripe + Xero APIs expose fee-level line items (feasibility · crit 4 · unc 2 · status: supported)
- `assumptions.md` — A1 · "bookkeepers distrust auto-match on tax-relevant data" · desirability · crit 5 · unc 4 · status: open · evidence: 1 user quote (2026-06-10) · test-plan: 5 concierge reconciliations, measure % overrides
- `value-prop-fit.md` — job "close the books, audit-clean" / pain "fees slip through" ↔ reliever "fee-level auto-match"; gain "close in <1h" ↔ creator "one-click reconcile"
- `pmf.md` — cluster: (1) ≥40% "very disappointed" survey · (2) month-2 retention curve flattens ≥30% · (3) qual: bookkeeper stops keeping the Excel backup — each with cheapest test noted
