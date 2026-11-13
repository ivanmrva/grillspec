# grill-product-vision — worked example

Illustrative: it shows the shape of the output, not a list to fill. The product turns customer-support transcripts into draft help-center articles; the project runs the `lite` profile.

> **Agent:** What do teams actually stop doing when they adopt this — using a knowledge-base tool like Notion, or writing docs by hand? *(I suspect the manual writing, which makes this "AI doc generation", not "another knowledge base".)*
> **User:** They keep Notion as the home. What they drop is the support lead writing articles from Zendesk tickets.
> **Agent:** Then the motion. Can one support lead try this alone on their own tickets, or must an admin connect Zendesk for the whole org first? *(Self-serve only works if one lead can connect and see value solo.)*
> **User:** One lead connects their own Zendesk and gets drafts the same day.

## Output — `vision.md`
- vision: every resolved ticket becomes a publishable help article.
- value prop: cut doc-writing from hours to one review pass. Relieves the top pain: no time to document fixes.
- who it is for: support leads on 10–50-agent teams, who hire it to keep the help center current without writing articles themselves.
- success metric: drafts published per active lead per week ≥ 3, eight weeks after launch · status: ratified
- kill-criterion: fewer than 20% of generated drafts published by week 12 after launch → stop · status: ratified

## Output — `scope.md`
| id | capability area | scope | phase |
|---|---|---|---|
| CA-01 | Ticket ingest (Zendesk) | in | MVP |
| CA-02 | Draft generation | in | MVP |
| CA-03 | Review and export to Notion | in | MVP |
| CA-04 | Multi-language drafts | in | deferred until a non-English customer signs |

Non-goals: hosting the knowledge base · live chat · support analytics.

## Output — `motion.md`
- motion: self-serve PLG
- rationale: one lead connects their own Zendesk and gets value on day one, so onboarding and billing are per-seat with no admin gate.
