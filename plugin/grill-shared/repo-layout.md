# Project structure — the global tree

```
<project>/
├── AGENTS.md             the one agent guide (written by derive-conventions)
├── CLAUDE.md             Claude Code adapter — exactly `@AGENTS.md`
├── GRILLSPEC-FEEDBACK.md feedback on this system (not the project); not part of spec/
├── .grillspec/           project settings (project.json) · vendored tools · gate config · waivers
├── .claude/settings.json Claude Code hook adapter (host-owned config only)
├── .codex/hooks.json     Codex hook adapter (host-owned config only)
├── spec/                 the specification (the tree below)
├── src/                  implementation code (mirrors the architecture's modules)
└── tests/                implementation tests
```

**Zones are exclusive.** Spec files live only under `spec/`; code only under the source and test trees; Grillspec's own project state only under `.grillspec/` (never copied into `.claude/` or `.codex/`); throwaway prototypes under `prototypes/`; the generated docs site under `docs-site/`. A project may root its code elsewhere (a `code/` monorepo); it then names its production tree in `.grillspec/grillspec-gate.json` and its test roots in `GRILLSPEC_TEST_ROOTS`.

**Spec and code are joined by tags, not by a matrix.** A test carries `@covers <ID>` for the acceptance criterion it proves; `check_task.py --trace` and `impact.py` read those tags, so the path from a requirement to the tests that guard it is computed from the tree. **Reference direction is upstream-only** (L0 foundation → L1 domain → L2 functional spec and requirements → L3 design system → L4 ux → L5 solution → L6 delivery → code); a file does not reference a layer below it. `lint_spec.py` enforces this.

## Project settings — `.grillspec/project.json`

| Setting | Values | Meaning |
|---|---|---|
| `profile` | `lite` · `standard` · `regulated` | how much spec the project carries (the tree below marks each area) |
| `delivery` | `trunk` · `pr` | how work lands: straight on the default branch with local verification, or through a pull request with the full CI gate |

`python3 ${CLAUDE_PLUGIN_ROOT}/tools/project_config.py` prints and sets them. With no file, tools assume `regulated` and `pr`.

| Profile | Fits | Areas |
|---|---|---|
| `lite` | a solo or pre-launch product | discovery · product vision · constraints · domain · functional spec · quality · architecture (strategy, stack, module map) · conventions · tasks |
| `standard` | a product that handles personal data, money, paid tiers, or a model whose quality must be gated | `lite` plus goals · system context · data · security · compliance · entitlements · integration · ml (AI products) · design system and ux (UI products) · the seven other solution areas as **decision records** |
| `regulated` | the documents themselves are a deliverable (an auditor, a regulator, another team) | every area, the solution areas in **full** |

Optional in every profile, run only on request: market · customer discovery · monetization · go-to-market · growth. They inform the founder; no build step reads them.

# Output tree — `spec/`

One leaf folder is the output of one skill. The only shared location is `adr/`. Folders appear as content settles; an area outside the profile, or one the product has no need for, simply stays absent. The marker after each line is the smallest profile the area belongs to (`opt` = optional).

```
spec/
│  glossary.md / actors.md   the reconciled system-wide views (the domain model owns the canonical vocabulary)
│  adr/                      every ADR, one file each: ADR-<PREFIX>-NNN.md (PREFIX = the area code)
│  _readiness.md             the per-area readiness view the conductor keeps
│  _human-input.md           the one queue of asks for the human (schema below)
│  _provisioning.md          the live credential register (schema below)
│
├── 01-discovery/           grill-problem-validation      the bets and how each would be tested          lite
├── 02-product/
│   ├── vision/             grill-product-vision          vision · scope · non-goals · phasing · motion    lite
│   ├── goals/              grill-goals                   north star · success metrics · kill criteria     standard
│   ├── customers/          grill-customer-discovery      segments · personas · jobs                        opt
│   └── market/             grill-market                  competitors · alternatives · sizing               opt
├── 03-constraints/         grill-constraints             mandates · stack · budget · regulatory bounds     lite
├── 03-system-context/      grill-system-context          actors · neighbour systems · interfaces (IF-)     standard
├── 04-domain/ddd/          grill-ddd                     strategic/* + tactical/<context>/*                lite
├── 05-functional-spec/     derive-functional             use-cases (UC-) + acceptance criteria (AC-)       lite
├── 06-requirements/
│   ├── quality/            grill-quality                 quality targets (NFR-) + what shapes the design (ASR-)  lite
│   ├── data/               grill-data-reqs               classes · retention · residency (DATA-)           standard
│   ├── integration/        grill-integration-reqs        per-boundary guarantees                           standard
│   ├── compliance/         grill-compliance              regimes → obligations (OBL-)                      standard
│   ├── entitlements/       grill-entitlements            tiers · gating · limits (ENTL-)                   standard
│   ├── security/           grill-security-reqs           authorization rules · threats (SEC-/THR-)         standard
│   └── ml/                 grill-ml-reqs                 quality bars · evals · fallback (ML-)             standard (AI only)
├── 07-design-system/       grill-design-system           tokens · components · a11y · voice (DS-)          standard (UI only)
├── 08-ux/                  grill-ux-reqs                 journeys (JRN-) · screens (SCR-) · states         standard (UI only)
│   ───────────────── architecture-readiness gate ─────────────────
├── 09-solution/
│   ├── arch/               derive-architecture           strategy · stack · module map (MOD-) · seams      lite
│   ├── data/               derive-data-architecture      storage decisions            (full: schema · migration)        standard
│   ├── api/                derive-api-contracts          seam index + policies (API-) (full: OpenAPI · AsyncAPI)        standard
│   ├── security/           derive-security-architecture  authn/authz · keys/secrets   (full: control register · supply chain)  standard
│   ├── infra-ops/          derive-infra-ops              environments · promotion · config matrix (full: IaC · DR · cost)  standard
│   ├── observability/      derive-observability          objectives (SLO-)            (full: telemetry · alerting · runbooks)  standard
│   ├── test/               derive-test-strategy          the tier contract            (full: evidence plan · test data)  standard
│   └── ml/                 derive-ml-architecture        eval gate · serving          (full: pipeline · monitoring)      standard (AI only)
│   ───────────────── implementation-readiness gate ─────────────────
├── 10-delivery/
│   ├── conventions/        derive-conventions            standards · boundary rules · commands · definition of done (+ AGENTS.md)
│   ├── tasks/              derive-tasks                  T-NNN.md task briefs + build-order.md
│   └── impl-design/        derive-impl-design            a short design note per critical slice, written just in time
│   ───────────────── delivery-readiness gate ─────────────────
│   (execution writes code, not spec: implement-task → source and tests)
├── 11-commercial/
│   ├── monetization/       grill-monetization            plans · prices                                    opt
│   ├── go-to-market/       grill-go-to-market            channels · launch                                 opt
│   └── growth/             grill-growth                  experiments (EXP-) · analytics events (AEV-)      opt
└── 12-operate/             deploy-release · migrate-data      dated operations records (deploys, migrations, incidents) + bootstrap.md
```

Below `regulated`, a solution area other than the architecture is a **decision record**: what code cannot tell a reader and what is costly to reverse. The description — table definitions, endpoint shapes, control lists, pipeline detail — lives in the artifact that enforces it, and once code exists that artifact is its source of truth (`derive-engine.md`).

**ADR prefix registry** (one per area):
`DDD` domain · `PROB` problem-validation · `VIS` product-vision · `CUST` customer-discovery · `MKT` market · `GOAL` goals · `CON` constraints · `CTX` system-context · `QUAL` quality · `DREQ` data-reqs · `IREQ` integration-reqs · `SREQ` security-reqs · `UX` ux-reqs · `DS` design-system · `COMP` compliance · `MLREQ` ml-reqs · `ENTL` entitlements · `FUNC` derive-functional · `ARCH` architecture · `DATA` data-architecture · `API` api-contracts · `SEC` security-architecture · `INFRA` infra-ops · `OBS` observability · `TEST` test-strategy · `IMPL` impl-design · `MLARCH` ml-architecture · `CONV` conventions · `TASK` tasks · `BUILD` implement-task · `REV` conformance-review · `MON` monetization · `GTM` go-to-market · `GRW` growth · `DIAG` diagnose · `REL` deploy-release · `MIG` migrate-data · `INC` operate-incident · `PROTO` prototype

## Spec-root files

Bets, risks and gaps live inline in the artifact they concern, each with a status; the conductor builds the cross-area views by reading the areas. Two files at the spec root hold live operational state and are exempt from the layer rule, because they join things from different layers:

| File | Holds | Shape |
|---|---|---|
| `_human-input.md` | the asks only a human can clear, batched so they can be cleared in one sitting | `## Ratify queue` — `\| topic/ID \| recommended value \| why \| status \|`, status `unconfirmed` → `ratified` / `overridden`; once settled the value is written into the owning artifact and the row removed. `## Blockers` — one entry per blocked task, led by its `T-` id: the blocker and what the human must do |
| `_provisioning.md` | one row per external credential or config key (matching `infra-ops/environments.md` where the project has it) | `\| key \| owner \| consuming tasks \| state \| evidence \|`, state `pending` / `provisioned`. `derive-tasks` seeds it and keeps existing state; an unattended run reads it to know which tasks must wait |

Both state what is open now. A cleared ask is removed, not annotated.

## Order within a stage

The folder numbers follow the dependency chain between stages. Within `06-requirements/` the order is partial: quality, data, integration, compliance and entitlements depend only on the domain and functional spec; security and ml each build on data. The design system (L3) precedes ux (L4), and both sit above requirements and below the solution. The areas under `11-commercial/` depend on nothing downstream and nothing depends on them.

**Gates:** desirability (soft) · architecture-readiness (in-profile requirements, design system and ux → solution) · implementation-readiness (solution → delivery prep) · delivery-readiness (delivery prep → execution) · per-task done. A gate counts only the areas the profile includes.

**The file set is closed.** A file under `spec/` sits at a path in this tree; content belongs in the artifact that owns it rather than a side file. `lint_spec.py` checks the paths, the headers, the references, the profile, and the timeless rule.

## Standalone and partial bundles
This is the full map. A standalone bundle ships only the skills it needs plus the shared engines they load; each skill writes its own deliverables to the location it is given or its default folder. Areas not shipped stay absent, which is valid: the linter checks that files sit at allowed paths, not that every area is filled. The conductor is optional — present, it routes and gates; absent, a skill is invoked directly.
