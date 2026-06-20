# Decision classes — what you DECIDE vs. what you ASK

Getting this classification right is the whole game. Wrong in one direction and you bury the user
in questions they hired the system to answer; wrong in the other and you silently bake in a constraint
that was theirs to set. **Default hard toward deciding — but never decide a fact you can't know.**
This is the **same judgment everywhere** — a **grill** skill's "recommend a default vs. genuinely
ask", a **derive** skill's "decide vs. escalate" (most of all `derive-architecture`), and an **exec**
skill's "proceed vs. raise a gap". Every engine loads this file; apply it to every fork.

## The convergence test (apply to every fork)
> Given **the recorded spec so far + sound engineering judgment**, would two
> equally-competent engineers necessarily reach the **same** answer?
- **Yes — one defensible answer follows from the spec + merit.** → **DECIDE.** Write it into the
  artifact; record it in the artifact. Don't ask.
- **No, and they'd diverge on a fact the user / org / platform holds that the spec doesn't carry**
  (a preference or a constraint). → **ASK.** This is the only thing you escalate.
- **No, but they'd diverge only on inconsequential taste** (two equivalent options, no later
  consequence). → **Pick the conventional one, record it in the artifact, move on.** Asking is noise.

The trap is the third case dressed as the second. "JSON or logfmt logs?" feels like a preference but
has no consequence the user cares about → pick one. "Which cloud region?" feels technical but turns on
data-residency law only the user knows → ask.

## You DECIDE these (write them; never ask) — settled by spec + engineering merit
Data model & persistence shape · identity & keying · module/seam boundaries (highest seam; reuse over
new) · pipeline/stage decomposition · algorithms & mechanisms (within the posture the ddd fixes) ·
error handling, retries, idempotency, concurrency · API & internal contracts · versioning & migration
mechanics · observability instrumentation (the *thresholds* may be an NFR/`SLO-`; the hooks are yours) ·
testing strategy · library choices **below the lock-in line** (swappable in days). Above that line it's
a stack choice → ASK.

## You ASK these (a preference or constraint the spec can't hold) — bundle, recommend a default, name what each gates
Target client platforms · scale/performance envelope *when the spec doesn't already imply it* · cost
ceiling & build-vs-buy tolerance · existing infra / vendor commitments / team skills · compliance
jurisdiction & residency *when the inputs don't fix it* · vendor choice among options that all clear
the technical bar · timeline & risk posture (MVP-fast vs build-for-scale) · security/UX trade-offs the
product is silent on. Each forks on a fact that isn't — and can't be — in the spec.

## Edge calls
- **The inputs already decided it.** If the spec settles a fork (residency, a posture constraint, a
  capacity bar, a hard/soft constraint in `context`), it is **not** a question — honor it. Re-asking a
  settled decision is the most common failure (the existing artifact is read first to prevent it).
- **The constraint is implied, not stated.** A consumer-mobile product implies a mobile client even if
  the ddd doesn't say "phones" — infer it, *state the inference*, ask only if the inference has a real
  fork (native vs PWA, with cost).
- **Decide the mechanism, not the parameter.** Decide the *shape* (e.g. "TTL-based expiry"); if the
  *value* (the TTL) turns on a business preference, take the requirement's value or surface only the
  parameter — not the whole mechanism.
- **A user-owned *value* is ratified, not invented.** A target/threshold/commitment — an SLA or
  availability number, a retention period, a risk/confidence threshold, an operating jurisdiction, a
  kill-criterion, a cloud/region/datastore commitment, an irreversible data deletion — is the user's
  or org's to set. **Propose a profiled default for them to ratify; proposing is not deciding.**
  Silently picking it is the costliest under-ask.
- **A domain *term* is elicited or ratified, not invented.** The name of a concept the domain already
  has a word for — an entity, command, event, role, state — is the user's to give, a fact the spec
  can't carry until they do: it is an ASK, never a free DECIDE, even though "default hard toward
  deciding" otherwise governs. **Propose the term for confirmation** ("I'll call this a *Booking* — is
  that your word?"); never silently christen domain vocabulary. Coining a label for a genuinely-new,
  unnamed concept is allowed, but **mark it coined** — an `inferred` term, or a `HOT-` hotspot if it is
  contested or you're unsure — so the expert can rename it (supersede, don't rename). The trap is the
  expert user whose established jargon you override with a generic synonym; harvest their term from any
  provided input and confirm it rather than re-eliciting. Silently inventing domain vocabulary is the
  costliest under-ask after silently picking a user-owned value, because a wrong-but-consistent
  ubiquitous language produces correct code for the wrong domain.
- **Hard-to-reverse but spec-settled.** Hard-to-reverse alone doesn't make it a user question — it makes
  it an **ADR**. You still decide it; you just document it with more care.

## Where each outcome lands
- **DECIDE (consequential):** write it into the artifact (or the code, for an exec skill); if it's hard-to-reverse *and* surprising *and* a real trade-off — also an **ADR** in `adr/` (rare).
- **DECIDE (inconsequential taste):** write it into the artifact. No ADR.
- **ASK:** raise a focused question; if it can wait, record a **Deferred** point in the artifact with an `at-task` trigger. The answer lands in the artifact (and, if meaningful, an ADR) so it's never re-asked.