# stu-shared-skills

A private **Claude plugin marketplace** for syncing a chosen set of skills between your two
Claude accounts. One GitHub repo is the single source of truth; both accounts install it and
either one can push updates the other picks up automatically.

## What's inside

A single plugin, **`stu-skills`**, containing these 8 skills:

| Skill | What it does |
|---|---|
| 10pm-curfew-creative-strategy-ops | Full-funnel paid-social creative toolkit |
| brand-performance-dashboard | Hostable HTML performance dashboard from media plan + metrics |
| client-call-synopsis | Granola client/partner calls → shareable Word synopsis |
| email-deliverability-cleaner | Clean/validate an email list before a send |
| girls-fact-post | Fact-style branded IG captions for @girls |
| girls-story-series | 10-slide interactive poll Story Series for @girls |
| motion-creative-benchmarks-2026 | Motion 2026 creative-testing benchmark data |
| skill-creator | Create, edit, optimize, and eval skills |

## One-time setup (do this once, from Account A)

1. Create an **empty private repo** on GitHub named `stu-shared-skills`.
2. From the unzipped folder:

   ```bash
   cd stu-shared-skills
   git init
   git add -A
   git commit -m "Initial shared skills bundle"
   git branch -M main
   git remote add origin git@github.com:<your-username>/stu-shared-skills.git
   git push -u origin main
   ```

## Install on each account (Account A and Account B)

In Claude Code / Cowork on each machine:

```
/plugin marketplace add <your-username>/stu-shared-skills
/plugin install stu-skills@stu-shared-skills
```

That's the only manual step per account. Both accounts now have all 8 skills.

## Editing & syncing

- **To change or add a skill:** edit files under `plugins/stu-skills/skills/`, then run
  `scripts/push-skills.sh` (or `git add -A && git commit && git push`).
- **To receive the other account's changes:** run `scripts/sync-skills.sh`, then in Claude
  run `/plugin marketplace update stu-shared-skills`.
- Because both accounts share one repo, syncing is **bidirectional** — whoever pushes last wins,
  standard git.

## Near-full automation

Point a scheduled task (cron, or a Claude scheduled task) at `scripts/sync-skills.sh` on each
machine — e.g. daily at 8am — so each account auto-pulls the latest before you start working.
After that, the only action you ever take is editing a skill and pushing.

## Adding more skills later

Drop another skill folder (its own directory with a `SKILL.md`) into
`plugins/stu-skills/skills/`, commit, and push. No manifest edits needed — the plugin picks up
every skill in that folder.

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
│        ├─ brand-performance-dashboard/
│        └─ … (6 more)
├─ scripts/
│  ├─ sync-skills.sh           # pull + refresh
│  └─ push-skills.sh           # commit + push
└─ README.md
```
