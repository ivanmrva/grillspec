# grill-monetization — worked example

Pricing a transcription API that already ships speaker-diarization and 12-language support:
> **Claude:** You bill by the minute today, but COGS scales with audio *seconds processed*, not seats — so per-seat would decouple price from cost. I'd meter on **audio-minutes transcribed**. Do you also resell the diarization, or is it bundled?
> **User:** Diarization is bundled on every call; languages beyond English are the upsell.

Recorded:
- `business-model.md` — usage-based API; value metric **audio-minutes transcribed** (selection screen: value-alignment 5, simplicity 4, measurability 5, predictability 3, expansion 5 — beat per-seat which scored 2 on value-alignment); axis **usage**; metering unit = 1 audio-minute, rounded up per request.
- `pricing.md` — **Starter** (prices `ENTL-001`) $0.018/min, English-only (fence: language pack), persona = solo dev, 2k free min/mo; **Pro** (prices `ENTL-002`) $0.012/min, all 12 languages + diarization (fence: language pack + priority queue), persona = Series-A product team; **Scale** (prices `ENTL-003`) $0.008/min, volume committed (fence: 250k-min/mo commit), persona = contact-center platform. Discovery basis: acceptable-price corridor $0.006–$0.020/min from 14 WTP interviews; Pro sits at the elasticity knee (~$0.012). Competitor benchmark $0.015/min (one input only).
- `unit-economics.md` — per-minute COGS $0.0041 (GPU inference + storage); markup floor $0.0066/min (never sold below); gross margin Pro 66%; LTV:CAC 4.1; CAC-payback 7 mo; NRR 119%; GRR 91%; Rule-of-40 = 31% growth + 12% margin = 43.
- `commitments.md` — **Starter** 99.0% uptime, community support, no credits; **Pro** 99.5%, <8 business-hr response, 10% credit per 0.1% breach; **Scale** 99.9%, <1 hr response, 25% credit. Uptime targets flow to the availability NFRs.

ADR: `adr/ADR-MON-001.md` — chose audio-minutes over per-seat metering.
