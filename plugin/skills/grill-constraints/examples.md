# grill-constraints — worked example

Illustrative: it shows the shape of the output, not a list to fill. The work is a patient-messaging feature added to a hospital's existing portal.

> **Agent:** Is "must be HIPAA-compliant" the binding constraint, or is it that PHI never leaves your Azure tenant? *(The first is a regime. The testable bound is data residency, and that is what removes design options, so I'd record it.)*
> **User:** Both apply. PHI stays in our Azure US tenant, with no external API calls carrying patient data. Security will not negotiate that.
> **Agent:** Who signs off that the data flow meets it before release — a named owner, not "Security"?
> **User:** Our CISO signs the data-flow review. And we are locked to the existing Okta for SSO.

## Output — `technical.md`
| constraint | hard/soft | source | carried by |
|---|---|---|---|
| PHI confined to the Azure US tenant; no external LLM API calls | hard | Security (CISO) | compliance |
| SMART-on-FHIR for EHR reads | hard | Epic integration | architecture |
| SSO through the existing Okta (OIDC) | hard | IT | architecture |
| TypeScript preferred for new services | soft | team skills | architecture |

## Output — `organizational.md`
| constraint | hard/soft | source |
|---|---|---|
| live before Q4 open enrollment | hard | Product VP |
| team of 4, no new hires | hard | budget |

## Output — `regulatory.md`
| regime | bound |
|---|---|
| HIPAA | US data residency; audit-logged access to PHI |
| state medical-records law | 7-year minimum retention |

## Output — `environment.md`
| system | owner | interface | commitment |
|---|---|---|---|
| Azure US tenant | Cloud team | private VNet | reuse |
| Okta | IT | OIDC | reuse |
| Epic EHR | Clinical IT | FHIR R4 | reuse |

A hospital has sign-off authorities and outside dependencies, so `stakeholders.md` (the CISO signs off the data-flow review) and `dependencies.md` (the Okta app registration, owned by IT) were written too. A solo project would stop at the four files above.
