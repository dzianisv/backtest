---
session: ses_12b8
updated: 2026-06-17T22:23:08.135Z
---

# Session Summary

## Goal
Research and select the best dynamic workflow plugin for OpenCode, then fork/create `dzianisv/opencode-dynamic-workflow` with fixes applied.

## Constraints & Preferences
- Plugin must work with OpenCode's plugin loader (requires default export)
- User prefers existing well-maintained solutions over rolling their own
- Local-first, bring-your-own-model preferred
- User wants script-as-orchestrator pattern (not prompt-only workflows)

## Progress
### Done
- [x] Diagnosed `opencode-drawer-workflows@1.6.0` silent load failure (named export vs required default export)
- [x] Applied fix: appended `export default WorkflowsPlugin;` to `/Users/engineer/.config/opencode/node_modules/opencode-drawer-workflows/dist/index.js`
- [x] Verified fix works via smoke test (workflow ID `wf_kvpflmoh` completed)
- [x] Forked `fredcamaral/drawers` to `dzianisv` (fork in progress on GitHub)
- [x] Researched competing OpenCode workflow plugins

### In Progress
- [ ] User asked to "research/review if there another plugins like this" — research completed, awaiting user decision on which to adopt

### Blocked
- Fork appeared as `dzianisv/drawers` not yet confirmed renamed to `opencode-dynamic-workflow`

## Key Decisions
- **Fix was a one-liner**: `export default WorkflowsPlugin;` — minimal patch, root cause confirmed
- **Original repo**: `fredcamaral/drawers` at `git+https://github.com/fredcamaral/drawers.git`

## Next Steps
1. Present research findings to user and get decision on which plugin to adopt
2. Either rename fork to `dzianisv/opencode-dynamic-workflow` and apply fix, OR switch to a better alternative
3. Update `opencode.json` plugin reference to point to chosen solution
4. Restart OpenCode to verify `workflow` tool loads

## Critical Context
- **Top competing plugins found:**
  - **`marcusrbrown/systematic`** — 22⭐, TypeScript, 40+ bundled skills, 50+ specialized agents, npm: `@fro.bot/systematic`, actively maintained (updated today). Structured engineering workflows, not script-as-orchestrator.
  - **`Suraj1235/open-dynamic-workflows`** — 3⭐, JavaScript, MIT, "the script is the orchestrator, not the model". Supports OpenCode, Codex, Antigravity, VS Code. Local daemon, QuickJS/WASM sandbox, bring-your-own-model (Anthropic/OpenAI/Ollama). Closest to Claude Code's dynamic workflows pattern.
  - **`534529531/ralph-flow`** — 13⭐, TypeScript, MIT, event-driven state machine with independent verification at every step. Forces AI to follow multi-step workflows with unbiased verification sessions. Pause/resume, JSON Lines logs, failure context on retry.
  - **`fredcamaral/drawers`** (current) — 4⭐, what we have installed. Ports Claude Code's background agents & workflows to OpenCode.
  - **`agustinusnathaniel/maestria`** — 0⭐, portable workflow patterns as plugin, MDX-based
  - **`deivid22srk/dynamic-workflows-skill`** — autonomous multi-agent orchestration for large-scale migrations/audits

- **Key differentiators:**
  - `open-dynamic-workflows`: script-as-orchestrator, fan-out parallel agents, critics verify, local-first — most aligned with user's `.agents/workflows/*.workflow.js` pattern
  - `ralph-flow`: state machine enforcement, independent verification sessions — best for "don't let AI skip steps"
  - `systematic`: most popular/polished, but more opinionated (bundled skills/agents)

## File Operations
### Read
- `/Users/engineer/.config/opencode/.opencode/package.json`
- `/Users/engineer/.config/opencode/dcp.jsonc`
- `/Users/engineer/.config/opencode/node_modules/@opencode-ai/plugin/dist/example.js`
- `/Users/engineer/.config/opencode/node_modules/@opencode-ai/plugin/package.json`
- `/Users/engineer/.config/opencode/node_modules/opencode-drawer-workflows/README.md`
- `/Users/engineer/.config/opencode/node_modules/opencode-drawer-workflows/dist/index.js`
- `/Users/engineer/.config/opencode/node_modules/opencode-drawer-workflows/dist/lib.js`
- `/Users/engineer/.config/opencode/node_modules/opencode-drawer-workflows/package.json`
- `/Users/engineer/.config/opencode/node_modules/opencode-scheduler/dist/index.js`
- `/Users/engineer/.config/opencode/node_modules/opencode-supermemory/dist/index.js`
- `/Users/engineer/.config/opencode/node_modules/opencode-supermemory/package.json`
- `/Users/engineer/.config/opencode/opencode.json`
- `/Users/engineer/.config/opencode/package.json`
- `/Users/engineer/workspace/backtest/.agents/knowledgebase/project-overview.md`
- `/Users/engineer/workspace/backtest/.agents/skills/signal-convergence-alert/convergence.py`
- `/Users/engineer/workspace/backtest/.agents/workflows/hedge-fund-committee.workflow.js`
- `/Users/engineer/workspace/backtest/.agents/workflows/pairwise-eval.workflow.js`
- `/Users/engineer/workspace/backtest/.agents/workflows/research-market.workflow.js`
- `/Users/engineer/workspace/backtest/.agents/workflows/research-trend-stocks.workflow.js`
- `/Users/engineer/workspace/backtest/.gitignore`
- `/Users/engineer/workspace/backtest/GOAL.md`
- `/Users/engineer/workspace/backtest/README.md`
- `/Users/engineer/workspace/backtest/scripts/opencode-workflow-runner.mjs`
- `/Users/engineer/workspace/backtest/strategy/README.md`
- `/Users/engineer/workspace/backtest/tests/opencode-workflow-runner.test.mjs`
- `/Users/engineer/workspace/backtest/thoughts/ledgers/CONTINUITY_ses_12b8.md`

### Modified
- `/Users/engineer/workspace/backtest/.agents/skills/signal-convergence-alert/convergence.py`
- `/Users/engineer/.config/opencode/node_modules/opencode-drawer-workflows/dist/index.js` (added `export default WorkflowsPlugin;`)
