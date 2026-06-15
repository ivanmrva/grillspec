---
name: conformance-review
description: >-
  The post-task review of generated code against OUR spec — run after each task, before the next. Two lenses: (A) conformance vs spec/architecture/contracts/security/NFR-evidence/traceability (blocking); (B) design health (advisory). Complements the native /code-review. Loads the shared exec core.
disable-model-invocation: true
argument-hint: the code and task to review against the spec
---

# conformance-review

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill: **the post-task review of generated code against the spec**, run after each task, before the next. **(A) conformance** (code vs spec, architecture, contracts, security, NFR-evidence, traceability — *blocking*); **(B) design health** (deepening opportunities — *advisory*). Distinct from, and complementary to, the native `/code-review`.

## Process
1. **Set the scope.** `changed` (default, every task — the task's changed code + its blast radius: callers, callees, seams) or `full` (preparing to ship — the whole codebase, still checked incrementally). The checks are identical; scope changes only *which* code they see.
2. **Run Lens A — conformance (blocking).** Architecture first (the hardest check): dependency direction & acyclicity, **each module's actual dependency direction matches its declared `role:`** (domain/driving-port/driven-port/adapter/application-service — once the implementation design records it), context-boundary integrity, layer isolation / ports & adapters, interface conformance, no structural rot, and a structural-regression scan of this diff. Then the spec: boundaries, contracts (`API-`), data model + residency/retention (`DATA-`), security rules & obligations (`SEC-`/`OBL-`), NFR/ASR with **test evidence, not an assertion**, and design-system conformance for UI. Confirm **traceability**: every referenced spec ID has implementing code + a passing test.
3. **Decide the verdict.** `VERDICT: PASS` only when Lens A is fully clean; else `VERDICT: FAIL — <blocking violations>` → fixed inside the boundaries. If the spec itself is wrong, raise a gap — never bend code around a bad spec, never edit the spec to match the code.
4. **Run Lens B — design health (advisory).** Surface shallow modules that could become deep (the deletion test; the interface is the test surface; one adapter = a hypothetical seam, two = a real one). Note friction organically. Never blocks the verdict.
5. **Record.** Write the traceability matrix + the review report (blocking-violation list + prioritized design-candidate list). Cheap candidates: refactor now under green; larger ones become focused-change tasks.

## Rules
- **Architecture conformance is first-class** — a failed-test re-run is exactly when shortcuts creep in, so check STRUCTURE every run, not just behavior: dependency direction & acyclicity · **role/direction match** (each module's real dependencies obey its declared `role:`, inward only) · context-boundary integrity (cross-context only via a published contract/event) · layer isolation & ports/adapters (persistence behind a port, no ORM/DTO leak, depend on interfaces) · interface conformance (no public surface beyond the implementation design) · no structural rot (no duplication, god-class, layer bypass, dead code, or hack to go green). The fitness functions enforce the deterministic part each run; this skill adds the **semantic** judgment they can't make.
- **Never pass on (blocking → back to implementation):** a crossed context/layer boundary · a dependency cycle · a module whose real dependencies contradict its declared `role:` direction · persistence/ORM leaking across a layer · an interface widened beyond the implementation design · duplicated logic or a layer bypass introduced to pass a test · a contract mismatch · an unenforced security rule/obligation · an NFR asserted but not evidenced · a schema/data change with no migration · an untraced spec ID.
- **Verdict:** `VERDICT: PASS` only when Lens A is fully clean (every referenced ID traced to code + a passing test); else `VERDICT: FAIL — <violations>`. Lens B never blocks.
- **Vs the native `/code-review`** — native = generic correctness/security/regressions; this = spec-divergence + traceability + architecture-health. Borrow its disciplines: verify each finding against the actual code before flagging; tag every finding by severity (`blocking` · `important` · `nit` · `suggestion`).
- **Lens B vocabulary** — module (interface + implementation) · interface (all a caller must know) · depth (much behavior behind a small interface; shallow = interface ≈ implementation in complexity) · **information leakage** (one design decision spread across N modules, so a change to it edits all N — a candidate to consolidate behind one module). Don't abstract before the second adapter; a rejected design candidate with a load-bearing reason becomes an ADR so future reviews don't re-suggest it.
- Code lives in the source tree, never in `spec/`.

## Output
Written under `delivery/verification/`:

| File / target | Captures | Format |
|---|---|---|
| `delivery/verification/traceability.md` | matrix: spec ID → T- → code/test path → pass | — |
| `delivery/verification/review-report.md` | blocking-violation list + prioritized design-candidate list + the verdict | — |

(+ ADRs → `adr/ADR-REV-NNN.md` — e.g. a rejected design-candidate with a load-bearing reason, so future reviews don't re-suggest it)
(no code, no spec changes)
Consumes: the produced code + the `T-NNN` package (or review set) + the referenced spec/arch IDs + the conventions + the domain model (glossary) + the area's ADRs.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
