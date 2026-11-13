# House rules — shared by every engine

The rules that are the same for interview, derivation, and execution. Each engine adds only what is specific to its kind of work.

## Earn your place
This is the first rule, and it outranks completeness. Write only the instructions, spec and constraints the reader needs and that lead to a better result. What a capable agent would do correctly anyway is not written down; a rule that restates the stack's idiom, a section that mirrors the code, a constraint with no failure behind it all cost attention on every read and return nothing.

Spec, constraints and gates exist where something reads them: a later step, a tool, or a person who will act on them. Before writing an area, a file, a section or a rule, name its reader. With no reader, leave it out and, where the absence could look like an oversight, say so in one line (`N/A — why`). The project's **profile** (`.grillspec/project.json`: `lite` · `standard` · `regulated`) sets the default scope; within it, depth still follows the product — a concern the product does not have gets no content. Growing the spec later, when a real need shows up, is cheap; keeping spec nobody reads consistent is not.

## The workspace is the source of truth
Work from the working tree as it exists now — the spec, code and tests on disk. Git history is the changelog, not a source to rebuild from: a removed file is gone, and "it used to work" is settled by the current tree. Git mechanics are fine (branching and committing per the project's delivery mode, `git bisect` to localise a regression, `git diff` to identify a change set). Stay inside the project folder unless the user hands you an input from elsewhere. Prior work that seems to be missing is a finding to surface, not something to restore.

## Artifacts are timeless
A file under `spec/` — and every ADR — states what is true now. A reader does not know it was generated, by what, or in how many passes, so it carries no trace of its own history: no dates of when something was decided or changed, no `new` / `previously` / `no longer` / `renamed from`, no note of what a pass added, moved, cut or deferred. A forward-looking scope choice is a timeless property (an exclusion ADR, or `deferred until <trigger>`). The same words stay legitimate as domain language (a `new booking`); `lint_spec.py` flags the document-history uses, and a genuine domain date carries `<!-- timeless: allow <why> -->`.

The same holds for structure. When a change lands, put it where it belongs and re-author the affected passage so the document reads as written in one pass: a changed statement is rewritten in place, and only new information becomes new content. Additions bolted onto the end, a parallel section beside the one that already owns the topic, or a "resolved" note left next to the old text all turn a document into a log. Operations records under `spec/12-operate/` are the exception: they are dated records by nature. (A report back to the user or orchestrator may of course say what changed — it is not a `spec/` artifact.)

## Write for the reader
The reader of a spec file is an engineer or an agent who has not seen this conversation and may open the file in the middle. Write so that each passage can be understood where it stands.

- **One home per fact.** State a fact once, in the area that owns it. Elsewhere, refer to it by ID with a few words saying what it is (`the 30-day retention rule, DATA-014`), so the sentence reads without a lookup and the fact cannot drift into two versions.
- **Tables for sets, prose for reasoning.** A set of like items with short values (fields, statuses, ID lists, actor × permission) is a table, ID in the first column. When a cell would need more than about two sentences, that item gets a short section of its own instead; reasons, trade-offs and anything with a "because" read better as a sentence or two than as fragments.
- **Plain and exact.** Use the project's agreed terms, the same word for the same thing every time, and concrete values over adjectives. Leave out sentences that carry no fact. Use emphasis for defined terms, field labels and IDs, not to mark importance or novelty.
- **Size follows content.** A file is as long as its facts need. If a file grows hard to read in one sitting, split it along a real seam (one context, one seam, one journey per file) rather than compressing it.

Every file under `spec/` opens with its `<!-- scope: … | excludes: … | format: … -->` header (code does not). Write your artifact to the location you are given, or — with none — your standalone default folder. ADRs go in the shared `adr/` folder, prefixed with your area code (`ADR-<AREA>-NNN`) so two skills never collide; an ADR holds the decision, its reason and the alternatives rejected, in a few sentences each. There are no side ledgers: an open point is resolved into the artifact or, if a deliberate choice, becomes an ADR. The output is the project's documentation and has no awareness of this system, so it names no skill or tool and does not describe how a file was produced. When you target an external standard, format or protocol (a WCAG level, OpenAPI, OAuth), use its current stable version unless a user or constraint pins another.

## Stable IDs
Every referenceable element carries a stable, type-prefixed ID; refer to it by ID; supersede an element rather than renaming or reusing its ID. Two mechanical rules the reference graph depends on:
- **Bare type prefix.** `AGG-250`, not `SUR-AGG-250` — tools key on the leading prefix, so a namespaced ID does not register as a definition. Disambiguate in the suffix (`AGG-SUR-250`) or by separate numeric bands per context.
- **The ID is the row key — first column.** A name-first row (`| pay-invoice | CMD-170 |`) does not register `CMD-170` as defined, and every later reference to it reads as undefined.

## System friction → plugin feedback
If you hit a defect or gap in this system itself — a check that is demonstrably wrong, an instruction you cannot satisfy, an ID type the tooling rejects — report it rather than working around it or writing it into your artifact: `python3 ${CLAUDE_PLUGIN_ROOT}/tools/plugin_feedback.py --add --kind bug|gap|improvement --component <this skill/the tool> --summary "…" --suggest "…" --evidence <file:line>`. It appends to `GRILLSPEC-FEEDBACK.md` at the project root, outside `spec/`. The bar is a real contradiction or an unsatisfiable rule, not a preference.
