# grill-market — worked example

Mapping the landscape for an AI contract-redlining tool aimed at in-house legal teams.

> **Claude:** What's the real alternative we displace — a competitor like Ironclad, or the status quo of a lawyer redlining in Word with a clause library? *(I'd treat Word + tracked-changes as the true incumbent; most teams have no AI tool at all, so "do nothing" is the competitor to beat.)*
> **User:** Honestly it's Word plus a folder of past contracts. Ironclad is CLM — it stores contracts, it doesn't redline them.
> **Claude:** Then where's the moat — what stops Ironclad from shipping redlining next quarter? *(If it's just "we're faster," that's not defensible; a data moat from accumulated redline decisions would be.)*
> **User:** Our edge is the labeled redline dataset — every accept/reject trains the suggestions. That compounds.

Recorded:
- `competitors.md` — matrix axes: redline-quality · CLM/storage · setup-time · price. Direct: LawGeex (redline ✓, no CLM, slow setup), Spellbook (redline ✓, GPT-based, no learning). Indirect/status-quo: Word + clause-library folder (free, manual, no consistency). Ironclad = adjacent CLM, not redlining
- `industry-forces.md` — new-entrant threat: HIGH (GPT wrappers cheap to build) · substitutes: MED (Word "good enough") · buyer power: MED (legal budgets tight) · supplier power: HIGH (foundation-model API dependency) · rivalry: rising · ecosystem note: CLM vendors are the likely acquirers/integrators
- `differentiation.md` — MOAT-1 data: labeled accept/reject redline corpus · evidence: 40k decisions logged · status: building · time/cost to replicate: 18+ mo of usage. MOAT-2 switching-cost: trained-on-your-playbook lock-in · status: weak early. Protected by retraining-from-scratch cost
- `sizing.md` — SOM = ACV $18k × reachable-ICP ~2,500 US mid-market in-house legal teams ≈ $45M · method: ICP count from LinkedIn legal-ops headcount filter; ACV from 3 LOIs · TAM (all corporate legal software) ~$30B as context · order-of-magnitude only
