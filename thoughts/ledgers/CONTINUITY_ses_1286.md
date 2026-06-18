---
session: ses_1286
updated: 2026-06-18T00:43:47.841Z
---

# Session Summary

## Goal
Fix the pairwise-eval workflow smoke test failure, then build a knowledgebase about Claude Code workflows and reference it in AGENTS.md so the team doesn't forget compatibility differences.

## Constraints & Preferences
- All 4 workflow files in `.agents/workflows/` must have explicit `model: MODEL` on every `agent()` call
- Knowledgebase entry must cover Claude Code native workflows (from https://code.claude.com/docs/en/workflows)
- AGENTS.md must reference the new KB entry
- Workflows in `.agents/workflows/` are OpenCode-only (`opencode-drawer-workflows` plugin); Claude Code uses `.claude/workflows/`

## Progress
### Done
- [x] Root-caused pairwise-eval failure: `github-copilot` provider fails model-list fetch → runner falls back to unsupported `gpt-5-mini` → `AI_APICallError: The requested model is not supported` → `status_error`, 0 tokens
- [x] Fixed all 4 workflow files — added `const MODEL = 'claude-sonnet-4'` + `model: MODEL` to every `agent()` call (25 total): pairwise-eval(1), hedge-fund-committee(6), research-market(8), research-trend-stocks(10)
- [x] Verified via `rg -c "model: MODEL"` — counts match total `agent(` counts per file
- [x] Created `.agents/knowledgebase/claude-code-workflows.md` — comprehensive reference covering primitives (`agent()`, `parallel()`, `step()`, `args`), commands (`/deep-research`, `/workflows`, `ultracode:`), limits (16 concurrent, 1000 max agents), and OpenCode↔Claude Code migration guide
- [x] Confirmed workflows are NOT Claude Code compatible (OpenCode plugin-specific runtime)

### In Progress
- [ ] Updating AGENTS.md to reference the new knowledgebase entry and note dual-runtime compatibility
- [ ] Was reading AGENTS.md lines 196-225 (research workflows section) to find insertion point

### Blocked
- (none)

## Key Decisions
- **`claude-sonnet-4` as explicit model**: Matches the reference fix in pairwise-eval; ensures reliability regardless of provider model-list fetch failures
- **KB in `.agents/knowledgebase/claude-code-workflows.md`**: Includes migration guide (OpenCode→Claude Code and reverse), comparison table, and all primitives
- **Not porting workflows to Claude Code format**: User asked for KB + AGENTS.md reference, not migration

## Next Steps
1. Insert a reference to `.agents/knowledgebase/claude-code-workflows.md` in AGENTS.md — likely near the "Research workflows" section (line 199+) or add a new section about workflow compatibility
2. Add a note in AGENTS.md that `.agents/workflows/*.workflow.js` files are OpenCode-only and Claude Code workflows go in `.claude/workflows/`
3. Run live verification of pairwise-eval workflow to confirm the model fix works
4. Update todos to mark remaining items complete

## Critical Context
- Plugin source: `opencode-drawer-workflows@git+https://github.com/dzianisv/opencode-dynamic-workflow.git` (v1.6.0)
- Plugin's `runner.launch()` is injected by OpenCode core, NOT part of the plugin — `lib.js` line 515
- Error logs found at `~/.local/share/opencode/log/2026-06-17T062027.log`
- Previous successful run evidence: `crypto/eval/pairwise-proof.txt` (B won 5-0)
- AGENTS.md workflow section starts at line 199; currently references `.agents/workflows/` without mentioning compatibility
- Claude Code workflow primitives (`agent()`, `parallel()`, `step()`, `args`) are API-compatible with OpenCode's but runtime/location differs

## File Operations
### Read
- `/Users/engineer/.config/opencode/node_modules/opencode-drawer-workflows/dist/lib.js`
- `/Users/engineer/.config/opencode/node_modules/opencode-drawer-workflows/package.json`
- `/Users/engineer/.config/opencode/opencode.json`
- `/Users/engineer/workspace/backtest/.agents/workflows/hedge-fund-committee.workflow.js`
- `/Users/engineer/workspace/backtest/.agents/workflows/pairwise-eval.workflow.js`
- `/Users/engineer/workspace/backtest/.agents/workflows/research-market.workflow.js`
- `/Users/engineer/workspace/backtest/.agents/workflows/research-trend-stocks.workflow.js`
- `/Users/engineer/workspace/backtest/.opencode/opencode.json`
- `/Users/engineer/workspace/backtest/AGENTS.md` (lines 196-225 most recently)
- `/Users/engineer/workspace/backtest/crypto/eval/pairwise-proof.txt`

### Modified
- `/Users/engineer/workspace/backtest/.agents/knowledgebase/claude-code-workflows.md` (created — full Claude Code workflows reference + migration guide)
- `/Users/engineer/workspace/backtest/.agents/workflows/pairwise-eval.workflow.js` (added `const MODEL` + `model: MODEL`)
- `/Users/engineer/workspace/backtest/.agents/workflows/hedge-fund-committee.workflow.js` (added `const MODEL` + `model: MODEL` to 6 calls)
- `/Users/engineer/workspace/backtest/.agents/workflows/research-market.workflow.js` (added `const MODEL` + `model: MODEL` to 8 calls)
- `/Users/engineer/workspace/backtest/.agents/workflows/research-trend-stocks.workflow.js` (added `const MODEL` + `model: MODEL` to 10 calls)
