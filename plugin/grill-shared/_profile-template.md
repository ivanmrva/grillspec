# Area profile — template (thin; the engine does the heavy lifting)

A profile is a thin layer on a shared engine. **Declare only what VARIES for this area** — the engine
(`grill-engine.md` / `derive-engine.md` / `exec-engine.md`) already owns everything universal: the
interview/derive/build method, the `<!-- scope | excludes | format -->` file header, the house rules for
writing, ADR placement, and the rule that the output names no skill or tool. State an engine rule in the
engine only, and each area fact once: the output table is the single enumeration of what the area writes.

Write a profile the way a brief for a capable colleague reads: what the area is for and who reads its
output, the few rules that are specific to it with the reason beside each, and what a larger project adds.
A rule without its reason gets applied rigidly; emphasis on every line reads as none; a long list of
prohibitions describes failure better than success. Keep exact wording only where a tool parses it (file
names, table columns, ID prefixes, cell vocabularies).

```
---
name: grill-<id>
description: >-
  <what it captures and when to use it, in plain words, under ~45 words — routing text, not a
  restatement of every output file>
disable-model-invocation: true
argument-hint: <what to hand it>
---

# grill-<id>

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/<engine>.md` first and follow it.** This skill applies that
method to **<Area>** — <one-line scope>.

## Method        ← OPTIONAL. The area's question order / approach — ONLY if it's a real sequence beyond
                   "fill in the files". If the process is just the list of things to capture, omit it:
                   the Output tree below IS the coverage.

## Depth by profile  ← what the area captures at each profile it is in scope for (`lite` · `standard` ·
                   `regulated`), or one line saying it is optional and run only on request. The core
                   first; what only a larger profile adds, marked as such.

## Rules         ← OPTIONAL. ONLY area-specific bars the engine doesn't carry — a gating trigger
                   ("GATED on real features to price"), a judgment rule ("authz is DEFAULT-DENY"), a
                   caveat ("coarse & revisable — don't over-ask"). NOT the file header, NOT house
                   style, NOT output content restated as a rule.

## Output        Heading is just `## Output` (no path in it). A lead-in `Written under `<folder>/`:` then a
                   markdown TABLE — the single place the outputs are enumerated:
                     | File | Captures | Format |
                   File = the `filename` (or path, for nested trees) · Captures = what it holds (plain prose)
                   · Format = its row/shape (the table columns · `Mermaid` · `numbered steps` · `—`). Below
                   the table as plain lines: `ADRs → adr/ADR-<AREA>-NNN.md`, any `glossary.md`/`actors.md` owned.
   Consumes: ...  ← OPTIONAL one line — the upstream artifacts it reads, named as CONCEPTS, never skills
                   ("the domain model", "the quality NFRs"). Omit for foundation areas with no upstream.

## Excludes      The scope fence — what belongs to other areas, named as concepts (→ compliance, → the
                 architecture), never as skills.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/<engine>.md`   (+ any other loadable file, e.g. examples.md)
```

Exec profiles (build/verify skills) keep their `## Process` steps and what is specific to their job —
what they check, what they report — and their output is code and short reports, not a spec artifact.
