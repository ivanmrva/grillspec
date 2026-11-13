# derive-engine — shared core for derivation skills (GENERATE, do not interview)

The shared method behind every derive profile. The profile's `SKILL.md` is the entrypoint and names what varies (source, scope, output slot); this engine is the judgment that is the same for all of them: what to write and what to leave to code, how to handle missing facts and emergent decisions, and how to change an artifact that already exists.

You write from the recorded spec, not from an interview. Everything you settle goes into your artifact; a costly-to-reverse decision also becomes an ADR in the shared `adr/` folder. On resume you re-read your artifact and continue from it.

**Shared rules:** load `${CLAUDE_PLUGIN_ROOT}/grill-shared/house-rules.md` (earn your place · the workspace as source of truth · timeless artifacts · writing for the reader · ID mechanics · plugin-feedback routing) and `${CLAUDE_PLUGIN_ROOT}/grill-shared/decision-classes.md` (decide vs. escalate — ask only for a fact the user, org or platform holds that the spec cannot carry).

## Decisions in the spec, descriptions in the artifact that enforces them
A solution-layer document earns its place by holding what code cannot tell a reader and what is costly to reverse: which datastore and how tenants are isolated, the versioning and idempotency policy of a seam, the identity provider and key management, the few objectives that page someone, the environments and how a change is promoted, the test tiers and their bars, the gate a model must pass and what happens when it fails. Write those once, as a short table or an ADR.

Detailed design is a description, and an executable artifact states it better and cannot drift from itself: table definitions live in the schema and migrations, endpoint shapes in the contract package, the control register in the authorization policy and its deny-path tests, dashboards and runbooks in instrumentation and alert configuration, pipeline detail in the workflows, test detail in the test configuration. Once code exists, the code is the source of truth for the description; the spec keeps the decision and the reason.

How much you write follows the project's profile (`python3 ${CLAUDE_PLUGIN_ROOT}/tools/project_config.py`, which also reports the delivery mode that workflow and pipeline decisions follow); your profile's `SKILL.md` says which files belong to which mode:

| Profile | The architecture area | The other solution areas |
|---|---|---|
| `lite` | strategy, stack, module map, ADRs | not written — their few decisions sit in the solution strategy and the conventions |
| `standard` | the full architecture | **decision mode** — the decision record only |
| `regulated` | the full architecture | **full mode** — the complete descriptive output, because the document itself is a deliverable someone outside the build reads |

## Generate from the spec, not from the user
Read the recorded source artifacts from the working tree as it exists now and generate. A fact the source does not carry is a gap (below), not a question for the user, and a missing source artifact is a gap too. Consider every upstream layer, not only your named inputs: they are where to start, not a boundary. Cite the IDs you actually use, because change propagation is computed from real references.

## Changing an artifact that exists
Your artifact is an ordinary authored document: it changes when its source changes or when building shows it was wrong, and whoever owns the area edits it in place. Read it first, then the source and what changed (the change set you are handed, or `git diff`), and apply the smallest change in meaning: keep every stable ID, accepted ADR, decision and still-true fact, and re-author the affected passages so the whole reads as written in one pass (the house rules' timeless rule). Regenerating the file wholesale churns IDs and drops decisions; appending turns it into a log. Name the IDs you touched in your hand-off, not in the artifact.

## A missing or contradictory source fact → record a gap with its timing
If a fact an interview should own is absent, ambiguous or contradictory, record the gap in your artifact against the element that needs it, and say when it must resolve:
- **resolve-now** — this artifact cannot be consistent without it → it is resolved in the source first.
- **defer** — a specific later consumer will need it → `Deferred`, with the trigger `at-task: <task/ID>`; it is forced to a decision when a task touching it is specified.
- **N/A** — legitimately absent (no UX for a headless slice) → `N/A` with the reason.

A fact is never invented to fill a cell: a retention period, a residency footprint or a quality number that upstream should have carried is a gap to log.

## An emergent decision → decide, and say so
A derivation can surface a decision the source could not anticipate — the architecture implies a queue nobody specified. That is an engineering decision with no source owner, not a missing fact. Apply the convergence test: decide it (the default), ask one focused question only if it forks on a fact the user or org holds, or take the conventional option when nothing depends on it. A resolved fork is simply visible in the artifact; one that is load-bearing, surprising and a real trade-off becomes an ADR with its rationale and the alternatives rejected, so a later run does not re-open it. A decision that adds capability (a queue, a cache, a service) also adds dependent content elsewhere; name it in your hand-off.

## A user-owned value or one-way door → a ratify-point
Some commitments belong to the user or organisation: a vendor, stack, cloud, region, datastore or identity-provider choice; the environment set and promotion path; a disaster-recovery tier with a real cost difference; an objective or SLA number the requirement left loose; tenant isolation; a deprecation window; a test-rigor bar; an accessibility level or locale scope when upstream is silent. Decide the merit pick, and surface it for a fast agree-or-override: the concrete recommended value with a one-line reason, written with `status: unconfirmed` and parked in `spec/_human-input.md` as a ratify-queue row (`| topic/ID | recommended value | why | status |`). The human sets the status to `ratified` or `overridden`; `lint_spec.py` flags a value still `unconfirmed` (an error once tasks exist). An ADR documents what you picked; it does not replace the human seeing it.

## IDs and boundaries
Consume the source by stable ID; every decision traces to the elements it serves. Respect bounded-context and layering boundaries — your output defines or specialises them. Mint new IDs per the house rules. Two points of ID semantics need care:
- **A trace or evidence table may be keyed on the upstream ID it traces.** A row led by a foreign ID — the `ASR-` your quality table realises, the `CMD-` an authorization matrix rules on — is a reference, not a re-definition. An ID is defined in its own area; everywhere else the same form is a reference.
- **Only Markdown row-key or `id:` definitions register.** An ID that lives only in a YAML contract (`x-grillspec-id`) is never a definition, so a reference to it reads as undefined — define the ID in Markdown (for a seam, in the API index).

## Completeness — both directions
You are done when every in-scope element of your artifact is derived and consistent and every requirement it must satisfy is addressed or has a logged gap or ADR. Check forward — every source element you must serve maps to something here — and backward — every element here traces to something the spec requires. Content with no upstream need is gold-plating: remove it. A deliberate omission is named with its reason (`deferred: caching until load is measured`).

## Your job's edges
You derive from whatever recorded artifacts you are given, behind no gate; with a required fact absent you record the gap and proceed on a justified default where you can. You write one artifact (plus its ADRs) to the given location, or — with none — your standalone default folder. You do not reconcile across other artifacts or chase dependents; whatever composes the areas does that. This keeps you usable on your own.
