# grill-monetization — worked example

Illustrative: it shows the shape of the output, not a list to fill. The product is a transcription API with speaker diarization and 12 languages; the user asked for pricing.

> **Agent:** You bill by the minute, and your cost scales with audio processed, not with seats, so per-seat pricing would cut the link between price and cost. I'd meter on audio-minutes transcribed. Is diarization resold or bundled?
> **User:** Bundled on every call. Languages beyond English are the upsell.
> **Agent:** Your 14 willingness-to-pay interviews put the acceptable corridor at $0.006–$0.020 a minute, with demand dropping off above $0.012. I'd put Pro there. Ratify?
> **User:** Yes.

## Output — `business-model.md`
- model: usage-based API
- value metric: audio-minutes transcribed. It tracks both the value the customer gets and our cost; per-seat does neither.
- axis: usage · metering unit: 1 audio-minute, rounded up per request

## Output — `pricing.md`
| plan | price | ENTL- tier | persona | basis | billing |
|---|---|---|---|---|---|
| Starter | $0.018/min, 2k free min a month | ENTL-001 | solo developer | top of the corridor | monthly, in arrears |
| Pro | $0.012/min | ENTL-002 | product team | the point where demand drops off | monthly, in arrears |
| Scale | $0.008/min with a 250k-min monthly commit | ENTL-003 | contact-centre platform | Untested | annual commit |

All three prices are ratified. Scale's basis is an untested bet: no interview covered that volume.

The competitor benchmark ($0.015/min) was one input. ADR-MON-001 records the choice of audio-minutes over per-seat metering.
