# generate-ui-prototype — worked example

A clickable, high-fidelity reference for **one UI slice** — the *customer-details* step of the "book a repair" journey — generated just-in-time for that slice, built from the **real design-system tokens & components**, every interaction state present, wired into the navigation the information architecture defines.

> **Claude:** This slice builds the customer-details screen, so I prototyped just that screen — rendered from the actual component variants (no ad-hoc styling), every interaction state, wired into the IA's nav so it clicks through in context, cross-linked to its `UC-`/`DS-` IDs. No global gallery: the site structure is already the IA spec + the design system, and the app shell is its own slice. Kept + versioned — the reference the coding task builds against, not a throwaway spike.

**The slice's screen — `2-customer-details.html`**, all interaction states:
- **empty** — blank form, primary CTA disabled
- **loading** — saved-addresses skeleton while fetching
- **success** — valid input, "Continue" enabled
- **error** — invalid postcode, inline message + field highlight (uses the `Input/error` component variant + `color.feedback.danger` token)
- **permission-denied** — read-only banner when the actor lacks `bookings:write`

**Wired into the IA:** clicks in from *branch/slot* and out to *confirm & pay* — that nav comes from the UX-requirements information architecture, not a generated index gallery.

**IDs this screen carries:** `JRN-07` (the book-a-repair journey it sits in) · `UC-BookRepair` (step 2 of the flow) · `DS-Input`, `DS-Button`, `DS-Banner` (the components instantiated).

`prototypes/ui/flows.md` (accretes as UI slices are built):

| journey (`JRN-`) | screens | UC- |
|---|---|---|
| `JRN-07` Book a repair | branch/slot → **customer-details** → confirm-pay → confirmed | UC-BookRepair |

(self-contained HTML, click-through with no build step; **regenerated for this slice's screen** on any UX-requirement or design-system change — a pure projection, never hand-maintained. No spec changes.)
