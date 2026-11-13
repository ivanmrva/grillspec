# generate-ui-prototype — worked example

Illustrative. One UI slice: the customer-details step of the "book a repair" journey. Only this slice's screen is prototyped; the app shell is its own slice, and the site structure already exists as the information architecture.

## `prototypes/ui/SCR-012-customer-details.html`

Rendered from the design system's own component variants and tokens, with every state the journey names:

| State | What the screen shows |
|---|---|
| empty | a blank form; the primary action is disabled |
| loading | a skeleton for the saved addresses while they load |
| success | valid input; "Continue" is enabled |
| error | an invalid postcode: inline message and field highlight (the `Input/error` variant, the `color.feedback.danger` token) |
| permission-denied | a read-only banner when the actor lacks `bookings:write` |

It is wired into the navigation: it opens from the branch-and-slot screen and continues to confirm-and-pay.

IDs it carries: `SCR-012` (the screen) · `JRN-07` (book a repair) · `UC-BookRepair` (step 2) · `DS-Input`, `DS-Button`, `DS-Banner`.

## `prototypes/ui/flows.md`

| journey | screen path | use-case |
|---|---|---|
| `JRN-07` Book a repair | SCR-011 branch and slot → SCR-012 customer details → SCR-013 confirm and pay → SCR-014 confirmed | UC-BookRepair |

## Review

The reviewer asked for the postcode error to appear on blur instead of on submit. That is a behaviour of the journey, so it was changed in the UX requirement first and the screen rebuilt from it. After approval the task brief reads:

| field | value |
|---|---|
| `ux` | JRN-07 · SCR-012 · states: empty · loading · success · error · permission-denied<br>prototype: `prototypes/ui/SCR-012-customer-details.html` |
| `prototype-review` | frozen |
