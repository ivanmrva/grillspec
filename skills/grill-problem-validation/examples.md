# grill-problem-validation — worked example

Illustrative: it shows the shape of the output, not a list to fill. The product is a tool that reconciles Stripe payouts against accounting ledgers for Shopify sellers.

> **Agent:** Who feels this most, and how often — the bookkeeper closing the month, or the founder spot-checking? *(I'd bet the bookkeeper, monthly, and that it is a painkiller: a wrong close means a restated tax filing.)*
> **User:** The bookkeeper, every month-end. They export both CSVs and match by hand in Excel. It takes a full day and still misses fees.
> **Agent:** So the catalyst is the close deadline. What pull is strong enough to beat the habit of "Excel already works"?
> **User:** Audit season. One mismatched payout cost a client a $4k penalty.

## Output — `problem.md`
- who hurts: SMB bookkeeper
- frequency × intensity: monthly × high (painkiller)
- current alternative: manual CSV match in Excel (about a day, misses processor fees)
- why-now: audit-season penalty exposure
- forces: push = $4k penalty + a day lost · pull = auto-match · anxiety = trusting automation on tax data · habit = "Excel works"

## Output — `bets.md`
| bet | type | criticality | uncertainty | status | test |
|---|---|---|---|---|---|
| Bookkeepers will trust auto-categorised matches | desirability | Critical | High | Untested | 5 concierge reconciliations; pass if under 20% of matches are overridden |
| Stripe and Xero APIs expose fee-level line items | feasibility | High | Low | Validated | read one live payout through both APIs |

The team has no discovery work under way, so the interview stops at these two files. Once interviews start, `assumptions.md` records each quote or datapoint against the bet it moves, and `pmf.md` names the signal cluster.
