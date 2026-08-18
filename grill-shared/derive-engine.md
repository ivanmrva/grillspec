# derive-engine — shared core for derivation skills (GENERATE, do not interview)

The shared method behind every derive profile. The profile's `SKILL.md` is the entrypoint and names what varies (source, scope, output slot); this engine is the judgment that's the same for all of them — how to handle missing facts and emergent decisions, and the house rules for what you write.

**Your output folder is your only memory**, and your output is a function of its source (`derived = f(source)`). Everything you decide goes into your derived artifact; meaningful, emergent decisions are ADRs in the shared `adr/` folder. On resume you re-read your artifact and continue; there is no side ledger.

**Shared rules:** load `${CLAUDE_PLUGIN_ROOT}/grill-shared/house-rules.md` (the workspace-only source fence · timeless artifacts · output discipline · ID mechanics · plugin-feedback routing) and `${CLAUDE_PLUGIN_ROOT}/grill-shared/decision-classes.md` (decide vs. escalate — apply it to every fork; ASK only a fact the user/org/platform holds that the spec can't carry).

## Derived artifacts are regenerate-only — NEVER hand-edited
Like generated code, your output changes only by this skill re-running against a changed source, never by hand-editing. You own your derived directory; nothing else writes to it. If a derived artifact needs to be different, the change belongs in the **source** (an authored or interview artifact); then you re-derive.

## Generate from the spec, not from the user
You do not interview anyone for facts. Read the recorded source artifacts from the working tree as it exists now and generate. A fact the source doesn't carry is a gap (below), not a question for the user — and a deleted or missing source artifact is a gap too, never something to reconstruct from git history (the house rules' fence; `git diff` to identify a change set on an incremental run is delta-detection, not a content source, and is fine).

## Incremental by default — diff, don't regenerate
On any run after the first, read your existing artifact first, then the source plus exactly what changed (the change set you're handed, or `git diff`), and apply the **minimal delta**. *Minimal* governs semantics, not structure: preserve every stable ID, accepted ADR, decision, and still-true fact — never churn, renumber, or drop them — while presenting the result as if the whole document were written from scratch today (integrate each change where it belongs and re-author the affected sections; the house rules' timeless-artifact rule governs the how). Don't blindly regenerate the file — that churns IDs and drops decisions — and don't blindly append — that accretes an incoherent log. When you re-derive, note the IDs you touched in your hand-off, never in the artifact.

## Missing / contradictory source FACT → record a gap WITH a resolution timing (never invent)
If a fact an interview should own is absent, ambiguous, or contradictory, record the gap in your artifact (against the element that needs it) and classify when it must resolve — not everything can be modelled upfront; edge cases especially surface late:
- **resolve-now** — needed for *this* artifact to be consistent at its maturity → resolve it in the source first.
- **defer** — not needed yet; a specific later consumer will need it → record **Deferred** with trigger `at-task: <task/ID>`; it is forced to a decision when a task touching it is specified.
- **N/A** — legitimately absent (no UX for a headless slice) → record N/A + rationale.

Never interview the user for facts, and never fabricate. (Emergent *decisions* are different — below.)

## Emergent DECISION (derive-and-ASK, then record) — different from a missing fact
A derivation can surface a decision the source couldn't anticipate — e.g. the architecture implies a message queue none was specified. That's not a missing fact (don't raise it as a gap); it's an engineering decision with no source owner. Classify it with the convergence test: decide (default hard toward this), ask one focused question (only if it forks on a fact the user or org holds), or pick the conventional option. A resolved fork is simply visible in the artifact; a load-bearing + surprising + real-trade-off decision becomes an **ADR** (rationale + alternatives rejected), so a re-run never re-asks it. Your existing artifact, its ADRs, and the source are all read before you decide or ask. A decision that adds capability (queue, cache, service) also adds dependent content and IDs elsewhere.

## A user-owned VALUE or one-way door is a RATIFY-POINT, never a silent pick
When a derivation must commit a value or one-way door the user/org owns — a vendor/stack/cloud/region/datastore/IdP commitment · the environment set & promotion path · a DR tier with a real cost delta · an SLO/SLA target the upstream NFR left loose · tenancy isolation · an API deprecation/sunset window · a test-rigor threshold (coverage/mutation) · a delivery-metric/DORA target · the a11y level or i18n locale scope when upstream is silent — **decide the merit pick, but surface it as a ratify-point**: always the concrete recommended value + a one-line why, framed for fast agree/override, never a blank. Write it with a `ratify`/`unconfirmed` status and park it in `spec/_human-input.md` as a scannable `<value> — <why> · agree? / override` entry so the human clears the batch in one pass. An ADR documents *what* you picked; it does not discharge the ratify — a one-way-door commitment the human never saw is an assumption, and the audit treats an un-ratified load-bearing value as a finding. Never *invent* a value the upstream should have carried (a retention period, a residency footprint, an NFR number): if it's missing upstream, that's a gap to log, not a number to coin.

## Honor IDs and boundaries
Consume the source by stable ID (`UC-`/`CMD-`/`NFR-`/…); every decision traces to the elements it satisfies. Respect bounded-context and layering boundaries — your output defines or specialises them. Mint new IDs per the house rules (bare type prefix, ID as the leading table column).

**Linter-safe ID forms.** The traceability spine is tokenized mechanically, so a few surface forms register an ID where you meant prose (a phantom undefined / out-of-area / downward error) and cost a remediation round. Keep to these — they read the same to a human and resolve cleanly:
- **A trace/evidence table MAY be keyed on the upstream ID it traces.** Leading a row with a *foreign* ID — the `ASR-` your `quality.md` realises, the `CMD-` an authz matrix rules on — is a row-key reference, not a re-definition; it resolves to the upstream definition. (You define an ID in *its own* area; everywhere else the same surface form is a reference.)
- **Cite an ADR by its bare ID** (`ADR-ARCH-007`), never as a link to its file. A `[…](adr/ADR-ARCH-007.md)` sitting after a reference word tokenizes the URL's `ADR-ARCH-007.md` as a phantom undefined ID.
- **An ID is `PREFIX-NUMBER` / `PREFIX-CODE-NUMBER`, never `PREFIX-word`.** Write "the API design", "the SLO burn-rate", "NFR evidence" — not `API-design`, `SLO-burn-rate`, `NFR-evidence`; a known prefix glued to a word tokenizes as a bogus ID.
- **No `area/word` slashes in prose.** `verification/cross-check`, `data/security` read as a downward path reference into a leaf area. Write "cross-check", "data and security".
- **Dot an ID suffix only for a real field** (`DATA-Customer.id`). Don't append `.method`/`.field`/`.port` to a non-data ID (`MOD-PORT-LLM.method`) — reference the ID bare and name the member in prose.
- **Only Markdown row-key / `id:` definitions register; a YAML contract's `x-grillspec-id` is reference-only.** An ID that lives *only* in `openapi.yaml`/`asyncapi.yaml` (a per-operation endpoint) is never a definition, so a cross-area keyword-reference to it reads as undefined — reference an MD-defined ID (e.g. the band-start), or also define it in MD.

## Completeness — verify BOTH directions, no gold-plating
Done when every in-scope element of your artifact is derived and consistent, and every ASR or obligation it must satisfy is addressed (or a gap/ADR is logged). Run the completeness critic both directions: **forward** — every source element you must serve maps to something here (no silent gap); **backward** — every element here traces to something the spec requires (no gold-plating, no invented capability). A genuine gap is named and justified ("deferred: caching until load is measured"), never silent.

## Your job's edges (input in, one derived artifact out)
**Consider every upstream layer, not just your named inputs.** Everything produced in earlier layers, plus any same-stage output whose derive-order is fixed before yours, is available context — derive from what's relevant. Your listed inputs are the primary, "start-here" sources, not an exhaustive or gating set. **Cite the IDs you actually use** — change-propagation is computed from real references, not from a declared list.

You derive from whatever recorded artifacts you're given, behind no gate. If a required source fact is genuinely absent, record the gap and proceed with a justified default where you can — never refuse, never invent. You write one derived artifact (plus its ADRs) to the given location, or — with none — your standalone default folder. You do not reconcile across other artifacts or chase dependents; if you are part of a larger spec, whatever composes the areas handles that. This keeps you usable on your own.
