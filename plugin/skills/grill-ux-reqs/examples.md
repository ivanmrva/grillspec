# grill-ux-reqs — worked example

Illustrative: it shows the shape of the output, not a list to fill. A freelancer invoicing app on the `standard` profile; the journey is "send an invoice".

> **Agent:** What does the freelancer see when a client's email bounces after they hit Send — a silent failure, or an error they can recover from? *(This is the rejection gap the use-case leaves open.)*
> **User:** It just looks sent. We want them told, with "fix email and resend".
> **Agent:** Sign-in: is there a one-time code typed from memory, or a puzzle? That fails accessible authentication; a passkey or an emailed magic link clears it. *(I'd default to a magic link. Ratify?)*
> **User:** Ratify the magic link.

## Output — `information-needs.md`
| id | screen | purpose | role | journeys |
|---|---|---|---|---|
| SCR-11 | Client picker | choose who is billed; shows contact and history | Freelancer | JRN-07 |
| SCR-12 | Invoice editor | line items and tax | Freelancer | JRN-07 |
| SCR-13 | Preview and send | check the total, send, see delivery status | Freelancer | JRN-07 |

Navigation: Clients · Invoices · Settings. Send sits under Invoices ▸ new. Help is top-right on every screen.

## Output — `journeys.md`
**JRN-07 · Freelancer · Send an invoice (UC-007)**
1. Pick the client (SCR-11) → 2. Add line items (SCR-12) → 3. Preview (SCR-13) → 4. Send (SCR-13).
- empty: no clients yet → "Add your first client" call to action.
- loading: Send shows the `DS-Button` loading state while the PDF renders.
- success: "Invoice sent to acme@…" and a timeline entry.
- error: delivery bounce → `DS-Banner` (danger): "Couldn't reach acme@… — fix email and resend".
- permission-denied: a read-only collaborator sees Send disabled with an "Owner only" tooltip.

## Output — `accessibility.md`
- target: the current WCAG at AA.
- accessible authentication: magic link, no cognitive test · consistent help: top-right on every screen · dragging: line-item reorder also has ↑/↓ buttons.
- inclusivity: plain-language amounts, Send reachable one-handed, legible in bright outdoor light.

The team runs no usability tests and ships in one locale, so the file sets no usability or i18n targets.
