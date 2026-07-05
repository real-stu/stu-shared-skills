---
name: motion-creative-benchmarks-2026
description: Authoritative reference for the Motion Creative Benchmarks 2026 report — $1.29B in Meta (Facebook/Instagram) ad spend, 578,750 creatives, 6,015 advertisers, Sept 2025–Jan 2026. Contains exact tables for hit rates, testing volume, winner/mid-range/loser splits, spend allocation by spend tier, testing volume by vertical, top-25%-vs-all comparisons, and format leaderboards (visual styles, hooks & headlines, asset types). Use WHENEVER Stu discusses creative testing benchmarks, hit rates, "how many creatives should we test", winner rates, creative volume, ad performance norms, spend tiers, or top ad formats/hooks — or wants industry data for a pitch deck, strategy memo, case study, campaign recap, UGC brief, or media plan justification. Also trigger on any mention of "Motion", "Motion report", "creative benchmarks", "Benchmarks 2026", or "10× winner", and when citing paid-social norms to a brand partner. Always pull exact figures from the references instead of recalling from memory.
---

# Motion Creative Benchmarks 2026 — Reference Skill

Privacy-safe, LLM-ready edition of Motion's Creative Benchmarks 2026 report. All data is aggregated and anonymous. This skill exists so benchmark figures cited in Stu's client work (pitches, strategy memos, dashboards, case studies, briefs) are **exact and sourced**, never approximated from memory.

## Dataset at a glance

- **Window:** Sept 1, 2025 – Jan 1, 2026 (spans BFCM and post-holiday reset)
- **Scope:** 578,750 creatives · 6,015 advertiser accounts · ~$1.29B realized spend · Facebook + Instagram only
- **Definitions:** Winner = spend ≥10× account median AND ≥$500. Mid-range = ≥28 days with spend, not a winner. Loser = turned off before day 28.
- **Spend tiers (monthly):** Micro <$10K · Small $10K–$50K · Medium $50K–$200K · Large $200K–$1M · Enterprise $1M+

## Headline numbers (verified, safe to cite)

- ~5% of ads spend ≥10× their account median; the 10× threshold ≈ the 92.3rd percentile of the ratio distribution (~7.7% of creatives above it). Expect roughly 1 winner per 10–13 creatives at best.
- Avg hit rate by tier: Micro 4.0% · Small 6.4% · Medium 8.1% · Large 8.6% · Enterprise 8.8% (CH-003)
- Avg testing volume (creatives/week): Micro 2.8 · Small 4.1 · Medium 6.6 · Large 11.2 · Enterprise 18.8 (CH-003)
- Spend concentration: ~55% of spend goes to winners, ~28% mid-range, ~17% losers; winner share of spend rises from ~23% (Micro) to ~64% (Enterprise) (CH-006)
- Portfolio composition: ~50–53% of creatives are losers, ~38–46% mid-range, ~4–8% winners, in every tier (CH-005)
- Top 25% of accounts (by winner count) test roughly 2–3× more creatives than tier average, e.g. Enterprise 54.6/wk vs 18.8/wk, yielding 10.4 vs 3.9 winners/month (CH-008)

## Reference files — read before citing specifics

- **`references/data-appendix.md`** — The exact tables (CH-001 through CH-012). Read this FIRST for any specific figure: hit rates, testing volume, portfolio/spend splits, vertical heatmap values, top visual styles, hooks & headlines, asset types. Never quote a table value without checking it here.
- **`references/report.md`** — Full narrative report with key findings (KF-001–KF-005), Part 1 (search for winners), Part 2 (anatomy of winning ads), methodology, glossary, and the "How to Use with an LLM" guardrails. Read for framing language, methodology details, or when writing prose that interprets the numbers.
- **`references/source-map.md`** — Provenance: which PDF page/notebook cell backs each chart and finding, suppression rules, and open questions (e.g., CH-006 Large-tier column-order ambiguity). Read when Stu or a client asks "where does this number come from" or when precision on sourcing matters.
- **`references/chart-specs.json`** — Machine-readable specs for all 12 charts (type, dimensions, measures, privacy flags). Use when rebuilding any of these charts in a dashboard, deck, or artifact.

## Hard rules when using this data

1. **Associations, not causation.** Say "accounts that test more surface more winners" — never "testing more causes more winners."
2. **No ROAS/revenue/conversion claims.** The dataset covers spend, winners, and hit rate only. Never extend findings to ROAS, CPA, or revenue.
3. **Meta only, dated window.** Findings are Facebook/Instagram, Sept 2025–Jan 2026 (BFCM-heavy). Do not apply to TikTok, organic social, or other windows without flagging the caveat. This matters for 10PM Curfew work, which is often organic/TikTok — when citing this report in that context, note it as paid Meta benchmark context, not a direct comparable.
4. **Respect suppression rules.** Segments under 50 accounts were suppressed (MIN_ACCOUNTS_FOR_FORMAT / MIN_ACCOUNTS_FOR_BRAND_CATEGORY = 50). Never invent values for suppressed cells or reconstruct point-level/advertiser-level data.
5. **Cite chart IDs.** When precision matters (decks, memos, anything client-facing), reference the chart ID (e.g., "CH-003, Motion Creative Benchmarks 2026") so figures are traceable.
6. **Flag the CH-006 caveat if citing Large tier spend allocation** — the PDF column order was ambiguous; the appendix uses Loser 17.1 / Mid 26.4 / Winner 56.5.

## Common use patterns for Stu

- **Pitch/strategy support:** "Only ~5% of ads become winners — creative volume is a structural advantage" framing, backed by CH-003/CH-008, to justify testing volume, UGC content pipelines, or always-on creative retainers.
- **Client expectation-setting:** Use tier hit rates to normalize "most ads won't be winners" and position 28-day evaluation windows before killing creative.
- **Format/hook recommendations:** Pull from CH-009 (visual styles), CH-011 (hooks & headlines), CH-012 (asset types) — always with the caveat that top formats vary by vertical (CH-010) and popularity ≠ spend capture.
- **Dashboards/decks:** Rebuild charts from chart-specs.json + appendix tables rather than eyeballing values.
