# grill-ux-reqs — worked example

UX requirements for a freelancer invoicing app — the "send an invoice" journey, its interaction states, and accessibility (the **design system is a separate area**; journeys reference it by `DS-` id).
> **Claude:** What does the freelancer see when a client's email bounces *after* they hit Send — a silent failure, or a recoverable error state? *(This is the rejection gap; an empty/loading/error trio is non-negotiable here.)*
> **User:** Today it just looks sent. We'd want them told, with a "fix email & resend".
> **Claude:** Sign-in: any one-time-code-from-memory or puzzle step? That fails accessible-authentication — a passkey or emailed magic-link clears it. *(I'd default to magic-link; ratify?)*
> **User:** Ratify magic-link.

## Output — `journeys.md`
**Role: Freelancer — "Send an invoice" (UC-007)**
1. Pick client → 2. Add line items → 3. Preview → 4. Send.
- **empty:** no clients yet → "Add your first client" CTA.
- **loading:** PDF render + send spinner on Send (renders the `DS-Button` loading state).
- **success:** "Invoice INV-1042 sent to acme@…" + timeline entry.
- **error:** delivery bounce → banner "Couldn't reach acme@… — fix email & resend" (`DS-Banner`, danger).
- **permission-denied:** read-only collaborator → Send disabled with "Owner-only" tooltip.

## Output — `information-needs.md`
- **Information architecture:** Clients · Invoices · Settings; Send lives under Invoices ▸ new; Help top-right on every screen.
- Per-step needs: client contact + history → line items + tax → preview total → send status.

## Output — `accessibility.md`
- **Target:** the current WCAG, at AA. Bars cleared: accessible-auth (magic-link, no cognitive test) · consistent-help (Help top-right every screen) · dragging (line-item reorder also has ↑/↓ buttons).
- **Inclusivity** (distinct from AA): plain-language amounts, one-handed reachable Send, legible in bright outdoor light.
- **i18n/l10n:** EN/ES/DE; currency + date per client locale; RTL-ready via logical properties.
- **Usability targets (UC-007):** effectiveness = task-completion ≥ 95% (unmoderated test) · efficiency = time-on-task ≤ 60 s + SEQ ≥ 6/7 · satisfaction = SUS ≥ 80.

The components/tokens these screens render (`DS-Button`, `DS-Banner`, `intent/danger`, `focus.ring`) are specified in the **design-system** area — referenced here by id, never defined here; a missing component is a gap raised there.

Recorded: every journey carries all five interaction states; three journey-level a11y bars cleared; inclusivity noted distinct from AA; usability framed effectiveness/efficiency/satisfaction with named instruments; the IA placed. Global UX only — the Send-screen pixel mockup belongs to the task slice, and the design system is its own area.
