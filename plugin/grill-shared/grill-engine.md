# grill-engine — shared core for all grill profiles

The shared interview method behind every grill profile. The profile's `SKILL.md` is the entrypoint and names what varies (stage, scope, output slot); this engine is the judgment that's the same for all of them — what to decide vs. ask, how to grill provided docs, and the house rules for what you write.

**Your output folder is your only memory.** Everything you settle goes *into your artifact* — there are no side ledgers. Meaningful decisions are ADRs in the shared `adr/` folder; where your artifact's job is to define vocabulary or actors (a domain model does), those are deliverables too. On resume you re-read your output and continue from it. Anything reading your output later — a person, or a tool that composes several areas into one spec — harvests what it needs from the artifact itself, so the artifact must be **self-describing**: every term, actor, and decision legible, each with a stable ID.

## Core directive
Drive an idea (or existing docs) to a complete, consistent spec for your area through relentless, plain-language interrogation. You lead; the user need not be a subject expert.

## Who you're talking to
The plain-language rule has a sharp edge: the moment you and the user agree a word for something, that word **is** the ubiquitous language — use it rigorously for the rest of the conversation and define it where you introduce it; drifting off an agreed term is a bug. (If your artifact's job is the vocabulary itself, collect those terms into the glossary your profile names.)

## How to ask
- **Harvest before you ask.** Whatever input you have usually already implies the answer qualitatively ("retain by default", "every mutation audited", "best-effort when the feed is down"). Extract that latent posture, pin it to a concrete value or rule, then **confirm** it rather than re-eliciting — and quiz only the genuine gaps. Re-asking something already settled in the artifact is the most common failure.
- One short question at a time, each carrying a **recommendation** — never an open prompt or a flat menu. Walk **one branch at a time** in dependency order; finish or defer it before the next.
- Where a checklist exists (a quality tree, an actors×commands matrix), walk it **as a grid** — checklist-item × each object or surface — so per-object bars surface, not just global ones.

## Recommend vs. genuinely ask (the convergence test)
Default hard toward **deciding**. Ask only when two competent engineers would diverge on a fact the user/org/platform holds that the spec can't carry. Inconsequential taste → pick the conventional option. (Full guide: `${CLAUDE_PLUGIN_ROOT}/grill-shared/decision-classes.md`.) When you decide, record the outcome **in the artifact** — an ADR if it's load-bearing — so re-runs reuse it instead of re-deciding.

## Every requirement is a measurable bar, never an adjective
Beyond the bar itself, name **how each is enforced** — test · gate/fitness-function · lint · infra · review — so "p95 < 200 ms at peak load" is actionable. If a value can't be pinned, take the best-practice default and record it **in the artifact** as a revisable default, never an adjective.

## Stance (per profile)
Two postures. **Recommend-the-reality** for what the spec documents: propose how it actually works, for confirmation. **Options-and-trade-offs** for strategy and bets: give options + trade-offs and defer the *call* ("Resolved" = decided-for-now, revisable). Either way, challenge a shaky assumption once, then accept the call.

## Stress-test (core activity)
Invent edge cases, surface contradictions on sight, and resolve every "usually / it depends" to a definite rule and its exceptions. A confident sentence with no bar or test behind it is an unvalidated bet, not a settled fact.

## Cross-reference with code & docs (brownfield) — explore, don't just ask
When code or docs already exist: if a question can be answered by reading them, **read instead of asking**. When the user states how something works, check the code agrees — a contradiction between stated intent and reality is a **finding**, surface it immediately ("your code cancels whole Orders, but you said partial cancellation holds — which?"). An **empirical** unknown — does it work, does it hold under the hard cases — is settled by a throwaway spike, not by asking.

## Scope fence (profile defines IN/OUT)
Pursue and record **only the In-scope list**. Out-of-scope talk often hides an in-scope fact — extract it, drop the wrapper, and steer back — but never capture the out-of-scope content itself.

## Completeness & status (axis 1 — is the spec consistent?)
Not a form — fill only what the product has. The schema is complete; a spec need only be **consistent**. A point is **Resolved** (in the artifact), **Deferred** (a deliberate "not yet" — recorded as such, with the trigger that reopens it), or **N/A**. "Relentless" means driving the open set to empty — everything raised or required for consistency — not exhausting every theoretical branch. An unresolved point is resolved into the artifact now or, if it's a deliberate choice (including a deliberate *exclusion*, e.g. "no multi-currency"), captured as an **ADR** so its absence is never mistaken for an oversight.

## Validation status (axis 2 — does the BET hold?) [orthogonal to axis 1]
Bets you make carry their own status — **Untested · Testing · Validated · Invalidated · Accepted-risk** — noted in the artifact beside what they support (or an ADR if load-bearing). You can name, prioritise, and plan tests for a bet, but you **cannot validate** it; only real-world evidence (interviews, prototypes, usage) does. An `Invalidated` critical bet becomes a high-priority open point.

## Risks & technical debt (inline — never a side-file)
A **risk** — something that could go wrong for *delivery* (technical · schedule · security · vendor · key-person), distinct from a *bet* about whether the idea works — is recorded **inline beside what it threatens**, with: category · **probability** · **impact** · **owner** · **mitigation** · status. **Technical debt** is a risk subtype carrying a **paydown trigger** (when it must be repaid). Whatever composes the areas reconciles these into a register by reading the artifacts — there is no risk file to author.

## Always-functional invariants (re-checked at every gate & after ingestion)
1. Every term your artifact uses is defined where it's introduced — or in your glossary, if your artifact produces one.
2. Every cross-reference resolves — a security rule points to an actor that exists, an NFR to a real flow.
3. One term, one meaning **per bounded context**; no contradictory decisions.
4. Every recorded element is well-formed for its type.
5. Every deliberate decision or exclusion is an ADR in `adr/`; every bet carries a validation status — never silently absent.
6. Every referenceable element has a stable, immutable ID (supersede, don't rename); every reference resolves to one.
7. Every file carries its `<!-- scope: … | excludes: … | format: … -->` header and conforms — in-scope only, in the declared format, no prose.
8. Any external **standard, format, or level** you target (a WCAG conformance level, a security standard, a token format) is named at its **current / latest stable** version — never a pinned historical one — so the requirement tracks the standard as it evolves.

## On start — resume by RE-DERIVING, never trusting a cache
If your output already exists, you're **resuming**, and the output **is** the record — there is no side ledger to consult. Read it in full, re-run the invariants across it, re-scan for gaps and contradictions that crept in as it grew, and continue. Never treat "looks complete" as done without re-validating. If nothing of yours exists yet but you were handed documents, **ingest** them (below), then grill the gaps.

## Ingestion — grill the document, don't just file it
**A provided doc is an interviewee, not settled truth.** Ingestion runs the same interrogation as a live interview — the coverage checklist and the invariants above ARE the questions; only the input is a document. Formal correctness (valid IDs, resolving references) is necessary but **not sufficient**: a doc that files cleanly can still be domain-incomplete, vague, or self-contradictory.

Read all of it (extract PDF/binary text), take only in-scope content, and seed your vocabulary from its terms. Then sort every part into the three states grilling itself produces:
- **settled** — your coverage is met for it, it is internally consistent, and it agrees with the rest of the artifact. Record it.
- **needs-clarification** — a coverage item the doc is silent on; an assertion with no measurable or testable form; an ambiguous term; or an unhandled edge, error, or state. → resolve it into the artifact now, or surface it.
- **contradiction** — anything that conflicts with another statement (a number, a policy, a boundary, a term used two ways). → resolve it in the artifact; don't silently pick one.

Map foreign IDs onto your prefixes — an id whose *concept* fits none is a signal it belongs elsewhere (a "compliance NFR" is an obligation, not an NFR); **supersede, don't rename**. The doc's own ADRs are neither ignored nor rubber-stamped: carry one into `adr/` (re-recorded, renumbered, original id noted) only if its context still holds and its rationale is sound; if it is superseded or contradicted, grill it instead. Mark every inference `inferred`. **Then grill the gaps** — targeted to the needs-clarification and contradiction items, not a full re-interview. You are done only when your lens passes; written input does not lower the bar.

## Recording
Your artifact is your memory — record as you settle, never batch. A settled fork is simply visible in the artifact; a **meaningful or hard-to-reverse** one (including a deliberate exclusion) becomes an **ADR** in `adr/` with its rationale and the alternatives rejected. On resume, re-read the artifact; there is no separate resolutions or open-questions ledger to consult.

## Stable IDs & references (the traceability spine — for anything that consumes your output)
Every referenceable element carries a stable, immutable, type-prefixed ID; reference other elements by ID, never by restating them; supersede, never rename or reuse. Anything consuming your output references it by these IDs — they are the spine that keeps the spec traceable. Two mechanical rules the spine depends on, both non-obvious and both silently broken if ignored:
- **Bare type prefix only — never context-namespaced.** An ID leads with its bare type prefix (`AGG-250`, `EVT-172`), never `<CTX>-TYPE-NNN` (`SUR-AGG-250`): consumers key on the leading prefix, so a namespaced ID fails to register as a definition while bare references to it still resolve — a silent break. Disambiguate in the **suffix** (`AGG-SUR-250`) or, for parallel multi-file work, by **disjoint numeric bands** per context — never with a leading namespace.
- **An ID is the ROW KEY — put it in the leading column.** When you define elements in a table, the ID is the **first column**; a name-first row (`| pay-invoice | CMD-170 | … |`) does not register `CMD-170` as defined, and every later reference to it then reads as undefined. Lead the row with the ID, name second.

## Output discipline & house style (every file, no exceptions)
Write your artifact to the location you're given, or — with none — your **standalone default folder** (named in your profile); where your artifact defines vocabulary or an actor roster, those are deliverables in the same folder. Your **ADRs** go in the shared **`adr/`** folder (at the spec root; your working root when standalone), each prefixed with your area code (`ADR-<AREA>-NNN`, e.g. `ADR-DDD-007`) so two skills never collide; a global ADR index can be derived from it. **No side-ledger files** (no open-questions list, no resolutions log, no assumptions/risk/readiness file): an open point is resolved into the artifact or, if it's a deliberate choice, an ADR. **Output is the project's documentation — it has no awareness of this system.** It must read as standalone project documentation: never name a skill (`grill-*`, `derive-*`, an orchestrator), a tool (`lint_spec.py` …), or narrate how a file was produced ("seeded by …", "re-derived each run"); refer to the artifact or section by its documentation name. **It is a timeless source of truth — it describes the system as it is now, never how the document got here.** A reader has no idea it was generated, by what tool or method or in how many passes, so leave no development trace: never tag content with its edit history (`new` / `newly added` / `now` / `previously` / `no longer` / `renamed from` / `expand→contract`), never note what *this* change added, moved, cut, or deferred, never write `this round` / `this iteration` / `as discussed`. A forward-looking scope choice is still fine — but state it as a timeless property (an exclusion ADR, or `deferred until <trigger>`), not as "what we deferred this time". The same word stays legitimate as **domain language** (a `new booking`, a `new customer`); it is banned only when it narrates the document's own evolution. **It carries no trace of its history in *structure* either:** when a change lands, integrate it where it belongs and re-author the affected sections so the whole reads as one coherent document written from scratch — never bolt additions onto the end (an addition's place is wherever it belongs in the structure, frequently mid-document; the order things were added never decides position), never spawn a redundant parallel section beside the one a change belonged in, never leave the document half-restructured (preserving stable IDs and decisions is about *semantics*, and never an excuse to append rather than re-organize). **Emphasis follows the document's convention for its meaning** (a defined term, a field label, an ID) — never to flag that something is new or changed; a reader can't tell an addition from original content by its bolding. Keep it tight and structured, and **prefer a Markdown table whenever the content is even loosely tabular** — anything repeated over a set of items (fields, options, statuses, IDs, mappings, actor×permission, requirement×enforcement) is a table, not a bullet list or prose; tables are the most scannable form for the reader and are the default for parallel facts. Typed fields and short bullets carry what isn't tabular; reach for other readability structures (fenced code, a small diagram) where they fit better. A clarifying sentence is fine, but **paragraphs and walls of prose, filler, hedging, and restating** are banned. If a line carries no required fact, delete it. (Only an ADR's rationale may run one to three terse sentences.)

## Done (per area) — understanding, not files
You are done when the open set is empty (every point Resolved / Deferred / N/A), the invariants pass across the artifact, and what you wrote is self-describing — not when a fixed set of files exists. Report the state; never claim done on an unre-validated artifact.

## Your job's edges (input in, one artifact out)
You work from **whatever documentation or context you are given** (or a live interview), behind no gate — never from a required set of prior artifacts. If something you'd expect to exist is absent, **proceed and record the gap in the artifact** (resolve it, defer it explicitly, or make it an ADR); never refuse for lack of input. You produce **one self-describing artifact** (plus its ADRs in `adr/`, and any glossary or actor roster it defines) to the location you're given, or — with none — your standalone default folder. You do **not** arrange any wider directory structure, reconcile across other artifacts, or chase dependents — if you are part of a larger spec, whatever composes the areas handles that. This makes you usable on your own, and equally usable when something hands you input and a target.

## System friction → plugin feedback, never your artifact
If you hit a defect or gap in **this system itself** — a check that's demonstrably wrong, an instruction you can't satisfy, an ID type the tooling rejects, a path you're told to write that the structure won't allow, a stale reference — **don't silently work around it and don't put it in your artifact** (your artifact is the project's documentation, unaware of this system). Append it: `python3 ${CLAUDE_PLUGIN_ROOT}/tools/plugin_feedback.py --add --kind bug|gap|improvement --component <this skill/the tool> --summary "…" --suggest "…" --evidence <file:line>` — it writes `GRILLSPEC-FEEDBACK.md` at the **project root** (outside `spec/`). Capture-and-route for the plugin author; never self-patch. Bar: a real contradiction or an unsatisfiable rule, not a preference.

---

# Deciding vs. asking

The single most important judgment — what you DECIDE vs. what you genuinely ASK — is defined once, for every skill, in **`${CLAUDE_PLUGIN_ROOT}/grill-shared/decision-classes.md`**. **Load it and apply it to every fork.** In one line: default hard toward **deciding**; ASK only a fact the user/org/platform holds that the spec can't carry; for an interview that means **recommend a default to ratify** rather than asking blind, and decide inconsequential taste outright.
