# grill-product-vision — worked example

Setting the vision for a tool that turns customer-support transcripts into draft help-center articles.

> **Claude:** Which alternative do teams actually drop when they adopt this — a knowledge-base tool like Notion, or just the status quo of writing docs by hand? *(I'd frame the category off whichever they abandon; I suspect it's the manual writing, which makes us "AI doc generation," not "another KB.")*
> **User:** They keep Notion as the home. What they drop is the support lead manually writing articles from Zendesk tickets.
> **Claude:** Then the motion question: does a support lead try this alone on their own tickets, or does it need an admin to wire up Zendesk for the whole org first? *(Self-serve PLG only works if one lead can connect and see value solo.)*
> **User:** One lead connects their own Zendesk and gets drafts the same day.

Recorded:
- `vision.md` — vision: "Every resolved ticket becomes a publishable help article, automatically." · value prop: "Cut doc-writing from hours to one review pass" → relieves top pain "support leads never have time to document fixes"
- `positioning.md` — competitive-alternatives: manual writing from Zendesk · unique-attributes: drafts from real resolved tickets · differentiated-value: doc reflects actual phrasing customers used · best-fit-segment: 10–50-agent support teams · market-category (derived): AI support-doc generation · one-liner: "For support leads who can't keep docs current, ArticleDraft is an AI doc generator that turns resolved tickets into review-ready articles; unlike writing them by hand, we draft from the real conversation."
- `scope.md` — in: Zendesk ingest, draft generation, review/edit, export to Notion · out: hosting the KB, live chat, analytics · MVP: Zendesk→draft→Notion export · near: Intercom source · deferred: multi-language
- `motion.md` — motion: self-serve PLG · rationale: one support lead connects own Zendesk OAuth and gets value day one; no org-wide admin gate, so onboarding and billing are per-seat self-serve
