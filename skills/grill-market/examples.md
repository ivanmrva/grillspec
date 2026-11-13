# grill-market — worked example

Illustrative: it shows the shape of the output, not a list to fill. The product is an AI contract-redlining tool for in-house legal teams.

> **Agent:** What do we really displace — a competitor like Ironclad, or a lawyer redlining in Word with a clause library? *(I'd treat Word with tracked changes as the incumbent. Most teams have no AI tool, so "do nothing" is the competitor to beat.)*
> **User:** It is Word plus a folder of past contracts. Ironclad stores contracts; it does not redline them.
> **Agent:** Then where is the moat — what stops Ironclad shipping redlining next quarter? *("We're faster" is not defensible; a data moat from accumulated redline decisions would be.)*
> **User:** The labelled redline dataset. Every accept or reject trains the suggestions, and that compounds.

## Output — `competitors.md`
| | redline quality | contract storage | setup time | price |
|---|---|---|---|---|
| LawGeex (direct) | good | none | slow | high |
| Spellbook (direct) | good, does not learn | none | fast | mid |
| Word + clause folder (status quo) | manual, inconsistent | folder | none | free |

Ironclad is adjacent: contract lifecycle management, not redlining.

## Output — `differentiation.md`
| moat | evidence / status | time or cost to replicate |
|---|---|---|
| data: labelled accept/reject redline corpus | 40k decisions logged · building | 18+ months of usage |
| switching cost: suggestions trained on the customer's own playbook | weak while the corpus is small | retraining from scratch |

The user had no sizing or market-entry decision open, so `industry-forces.md` and `sizing.md` were not written.
