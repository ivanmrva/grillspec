# grill-constraints — worked example

Pinning the bounds for a patient-messaging feature added to a hospital's existing portal.

> **Claude:** Is "must be HIPAA-compliant" the real constraint, or is the binding one that PHI never leaves your Azure tenant — air-gapped from any third-party LLM? *(The first is a regime; the testable bound is data-residency. I'd record the residency rule, since that's what kills design options.)*
> **User:** Both apply, but yes — PHI must stay in our Azure US tenant, no external API calls with patient data. That's non-negotiable from Security.
> **Claude:** Who signs off that the data-flow meets that before release — a named owner, not "Security"? *(The release checklist needs a real person to ask.)*
> **User:** Our CISO, Dana Whitfield, signs the data-flow review. And we're locked to the existing Okta for SSO.

Recorded:
- `technical.md` — C-T1 PHI confined to Azure US tenant, no external LLM API calls · hard · source: Security/CISO. C-T2 implement SMART-on-FHIR for EHR read · hard · source: Epic integration. C-T3 SSO via existing Okta OIDC · hard · source: IT
- `organizational.md` — C-O1 ship before Q4 open-enrollment (2026-10-01) · hard · source: Product VP. C-O2 team of 4, no new hires · hard · source: budget
- `stakeholders.md` — Dana Whitfield (CISO) · Accountable · signs-off-for: security & data-flow review. Product VP · Responsible · signs-off-for: scope/launch. Compliance officer · Consulted · signs-off-for: HIPAA attestation
- `conventions.md` — CV-1 patient-facing copy at ≤8th-grade reading level · source: health-literacy policy. CV-2 dates in patient UI as MM/DD/YYYY · source: org style guide
- `regulatory.md` — HIPAA (PHI handling) · bound: data-residency US + audit-logged access. State med-records retention · bound: 7-year minimum
- `environment.md` — Azure US tenant · owner: Cloud team · interface: private VNet · commitment: reuse. Okta · owner: IT · interface: OIDC · reuse. Epic EHR · owner: Clinical IT · interface: FHIR R4 · reuse
- `assumptions.md` — A1 "Epic FHIR exposes message-thread write scope" · owner: Clinical IT · if-false→ build a custom HL7 bridge (+6 wks)
- `dependencies.md` — D1 Okta app registration · owner: IT · needed-by: 2026-08-15. D2 Security data-flow sign-off · owner: CISO · needed-by: pre-launch
