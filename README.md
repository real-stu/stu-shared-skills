# stu-shared-skills

A **public Claude plugin marketplace** for syncing a chosen set of skills between Stu's two
Claude accounts. One GitHub repo is the single source of truth: both accounts add it and either
one can push updates the other picks up.

## What's inside

A single plugin, **`stu-skills`**, containing these 6 skills:

| Skill | What it does |
|---|---|
| 10pm-curfew-creative-strategy-ops | Full-funnel paid-social creative toolkit |
| email-deliverability-cleaner | Clean/validate an email list before a send |
| girls-fact-post | Fact-style branded IG captions for @girls |
| girls-story-series | 10-slide interactive poll Story Series for @girls |
| motion-creative-benchmarks-2026 | Motion 2026 creative-testing benchmark data |
| skill-creator | Create, edit, optimize, and eval skills |

## Install on each account (Cowork desktop app)

Do this once per account:

1. Open **Customize → Plugins** in the sidebar.
2. Click **+ → Add from a repository**.
3. Enter `real-stu/stu-shared-skills` (or `https://github.com/real-stu/stu-shared-skills`) and **Sync**.
4. Find **Stu skills** and click **Install**.

That's the only manual step per account. Both accounts now have all 6 skills.

## Editing & syncing

- **To change a skill:** on GitHub, open the file under `plugins/stu-skills/skills/`, click the
  pencil icon, edit, and **Commit changes**.
- **To add a new skill:** upload its folder (its own directory with a `SKILL.md`) into
  `plugins/stu-skills/skills/` and commit. No manifest edits needed — the plugin picks up every
  skill in that folder.
- **To pull the latest on an account:** open the **Stu skills** plugin, use its **⋮** menu, and
  choose sync/update.
- Because both accounts share one repo, syncing is **bidirectional** — whoever pushes last wins.

## A note on visibility

This repo is **public**, so anything committed here is readable by anyone with the link. Keep
skills that contain pricing, rate cards, media plans, or client-confidential material OUT of this
repo. (That's why brand-performance-dashboard and client-call-synopsis were intentionally left
out.)

## Repo structure

```
stu-shared-skills/
├─ .claude-plugin/
│  └─ marketplace.json        # declares the marketplace + the stu-skills plugin
├─ plugins/
│  └─ stu-skills/
│     ├─ .claude-plugin/
│     │  └─ plugin.json        # plugin manifest
│     └─ skills/               # one folder per skill
│        ├─ 10pm-curfew-creative-strategy-ops/
│        ├─ email-deliverability-cleaner/
│        ├─ girls-fact-post/
│        ├─ girls-story-series/
│        ├─ motion-creative-benchmarks-2026/
│        └─ skill-creator/
├─ scripts/
│  ├─ sync-skills.sh           # optional: git pull + refresh
│  └─ push-skills.sh           # optional: git commit + push
└─ README.md
```
