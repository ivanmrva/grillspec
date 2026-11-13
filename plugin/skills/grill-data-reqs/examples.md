# grill-data-reqs — worked example

Illustrative: it shows the shape of the output, not a list to fill. The class is the customer contact record captured when a repair is booked.

> **Agent:** This holds name, address and phone, so it is personal data. What are the TTL and the deletion trigger — keep it forever, or drop it once the warranty window closes? *(I'd tie retention to the obligation: 24 months after job completion, matching the warranty period.)*
> **User:** 24 months after the job closes, then purge.
> **Agent:** Where does it physically live, and whose law governs access — the same answer, or split? *(I'd store it in Frankfurt, but the parent company is US-incorporated, so sovereignty differs from residency.)*
> **User:** Stored in Frankfurt; the parent is US, so yes, the US can compel access.

## Output — `data-classes.md`
| id | category | classification | retention | residency | tenancy | ownership |
|---|---|---|---|---|---|---|
| DATA-003 | Customer contact record | PII | 24 months after job closed, then purge | eu-central-1 (Frankfurt) | per booking branch | Branch Operations |

### DATA-003 Customer contact record
- consent: lawful basis is contract performance. Marketing contact is a separate consent, withdrawn through a self-serve opt-out and asked again when the marketing purpose changes.
- sovereignty: US. The parent company is US-incorporated and subject to lawful compulsion; this needs counsel.
- lineage: origin AGG-201 Booking · no derivation · downstream DATA-021 (invoicing).

On the `standard` profile no decision depends on volume, integrity or data quality here, so those fields are absent.
