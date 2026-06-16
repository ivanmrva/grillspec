# derive-engine — shared core for derivation skills (GENERATE, do not interview)

The shared method behind every derive profile. The profile's `SKILL.md` is the entrypoint and names what varies (source, scope, output slot); this engine is the judgment that's the same for all of them — how to handle missing facts and emergent decisions, and the house rules for what you write.

**Your output folder is your only memory**, and your output is a **function of its source** (`derived = f(source)`). Everything you decide goes into your derived artifact; meaningful, emergent decisions are ADRs in the shared `adr/` folder. On resume you re-read your artifact and continue; there is no side ledger.

## Derived artifacts are regenerate-only — they are NEVER hand-edited
Like generated code, your output changes only by **this skill re-running** against a changed source, never by hand-editing. You own your derived directory; nothing else writes to it. If a derived artifact needs to be different, the change belongs in the **source** (an authored or interview artifact); then you re-derive.

## Generate from the spec, not from the user
You do **not** interview anyone for facts. Read the recorded source artifacts and generate. A fact the source doesn't carry is a gap (below), not a question for the user.

## Incremental by default — diff, don't regenerate
On any run after the first, **read your existing artifact first**, then the source plus exactly what changed (the change set you're handed, or `git diff`), and apply the **minimal delta** — preserve existing IDs, accepted ADRs, and untouched content verbatim; touch only what the change affects. Never regenerate a file from scratch: it churns IDs, drops decisions, and breaks traceability. When you re-derive, note the IDs you touched.

## Missing / contradictory source FACT → record a gap WITH a resolution timing (never invent)
If a *fact an interview should own* is absent, ambiguous, or contradictory, record the gap **in your artifact** (against the element that needs it) and **classify when it must resolve** — not everything can be modelled upfront; edge cases especially surface late:
- **resolve-now** — needed for *this* artifact to be consistent at its maturity → resolve it in the source first.
- **defer** — not needed yet; a specific later consumer will need it → record **Deferred** with trigger `at-task: <task/ID>`; it is forced to a decision when a task touching it is specified.
- **N/A** — legitimately absent (no UX for a headless slice) → record N/A + rationale.

Never interview the user for facts, and never fabricate. (Emergent *decisions* are different — see below.)

## Emergent DECISION (derive-and-ASK, then record) — different from a missing fact
A derivation can surface a **decision the source couldn't anticipate** — e.g. the architecture implies a message queue none was specified. That's not a missing fact (don't raise it as a gap); it's an engineering decision with no source owner. Classify it with the convergence test (`${CLAUDE_PLUGIN_ROOT}/grill-shared/decision-classes.md`): decide (default hard toward this), ask one focused question (only if it forks on a fact the user or org holds), or pick the conventional option. **A resolved fork is simply visible in the artifact; a load-bearing + surprising + real-trade-off decision becomes an ADR** in `adr/` (rationale + alternatives rejected), so a re-run never re-asks it. Your existing artifact, its ADRs, and the source are all read **before** you decide or ask. A decision that adds capability (queue, cache, service) also adds dependent content and IDs elsewhere.

## Honor IDs and boundaries
Consume the source by **stable ID** (`UC-`/`CMD-`/`NFR-`/…); every decision traces to the elements it satisfies. Respect bounded-context and layering boundaries — your output defines or specialises them. When you mint a new ID: lead it with a **bare type prefix** (`API-12`, never `<CTX>-API-12` — a context-namespaced ID silently fails to register while bare references to it resolve), and where you define elements in a table, put the **ID in the leading column** (the row key — a name-first row leaves the ID unregistered and its references reading as undefined).

## Standards: target the latest stable, never a pinned version
When your output adopts an external **standard, format, protocol, or RFC** (OpenAPI, AsyncAPI, WCAG, OAuth/OIDC, DTCG, HTTP problem-details, …), target its **latest stable release at generation time** and refer to it as "the current / latest stable" — never bake a historical version number into the spec, so the output tracks the standard as it evolves. Pin a specific version only when a user/constraint requires it (e.g. a regulator naming one).

## Completeness — verify BOTH directions, no gold-plating
Done when every in-scope element of your artifact is derived and consistent, and every ASR or obligation it must satisfy is addressed (or a gap/ADR is logged). Run the completeness critic **both directions**: **forward** — every source element you must serve maps to something here (no silent gap); **backward** — every element here traces to something the spec requires (no gold-plating, no invented capability). A genuine gap is named and justified ("deferred: caching until load is measured"), never silent.

## Output discipline & house style
Write your derived artifact to the location you're given, or your standalone default folder; your **ADRs** go in the shared **`adr/`** folder (at the spec root; your working root when standalone), each prefixed with your area code (`ADR-<AREA>-NNN`) so two skills never collide. Every file opens with a `<!-- scope: … | excludes: … | format: … -->` header; keep it tight and structured in the ubiquitous language, and **prefer a Markdown table whenever the content is even loosely tabular** — anything repeated over a set of items (fields, options, statuses, IDs, mappings, element×trace) is a table, not a bullet list or prose, because tables are the most scannable form for the reader. Typed fields and short bullets carry what isn't tabular; reach for other readability structures (fenced code, a small diagram) where they fit better — prose to clarify, not walls. **No side-ledger files** — a resolved fork lives in the artifact, a meaningful one in an ADR; there is no resolutions or open-questions log. Your output **is the user's documentation**: never name a skill or tool, or narrate how a file was produced ("derived by …").

## Your job's edges (input in, one derived artifact out)
You derive from **whatever recorded artifacts you're given**, behind no gate. If a required source fact is genuinely absent, **record the gap and proceed with a justified default where you can** — never refuse, never invent. You write **one derived artifact** (plus its ADRs in `adr/`) to the given location, or — with none — your standalone default folder. You do not reconcile across other artifacts or chase dependents; if you are part of a larger spec, whatever composes the areas handles that. This keeps you usable on your own.

## System friction → plugin feedback, never your artifact
If you hit a defect or gap in **this system itself** — a check that's demonstrably wrong, an instruction you can't satisfy, an ID type the tooling rejects, a path you're told to write that the structure won't allow — **don't silently work around it and don't put it in your artifact**. Append it: `python3 ${CLAUDE_PLUGIN_ROOT}/tools/plugin_feedback.py --add --kind bug|gap|improvement --component <this skill/the tool> --summary "…" --suggest "…" --evidence <file:line>` — it writes `GRILLSPEC-FEEDBACK.md` at the **project root** (outside `spec/`). Capture-and-route for the plugin author; never self-patch.

---

# Deciding vs. asking

What you DECIDE vs. what you ASK is defined once, for every skill, in **`${CLAUDE_PLUGIN_ROOT}/grill-shared/decision-classes.md`**. **Load it and apply it to every fork.** In one line: default hard toward **deciding** from the spec; ASK only a fact the user/org/platform holds that the spec can't carry; pick the conventional option for inconsequential taste.
