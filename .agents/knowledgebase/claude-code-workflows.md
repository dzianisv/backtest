# Claude Code Dynamic Workflows — Reference

> Source: https://code.claude.com/docs/en/workflows (fetched 2026-06-17)
> Requires: Claude Code v2.1.154+. Available on Pro/Max/Team/Enterprise.

## What it is

A **dynamic workflow** is a JavaScript script that orchestrates subagents at scale.
Claude writes the script, a runtime executes it in the background, your session stays responsive.
Intermediate results stay in script variables (not Claude's context window).

## When to use (vs subagents / skills / agent teams)

| | Subagents | Skills | Agent teams | **Workflows** |
|---|---|---|---|---|
| Who decides next | Claude | Claude | Lead agent | **The script** |
| Results live in | Context window | Context window | Shared task list | **Script variables** |
| Repeatable | Worker def | Instructions | Team def | **The orchestration** |
| Scale | Few per turn | Same | Handful | **Dozens to hundreds** |

## Key commands

- `/deep-research <question>` — bundled research workflow
- `/workflows` — list/manage running and completed workflows
- `/effort ultracode` — auto-workflow for every substantive task
- `ultracode:` keyword in prompt — trigger a workflow for one task
- Press `s` in `/workflows` view to save as a reusable `/command`

## Script primitives (available inside workflow scripts)

The runtime provides these globals to workflow scripts:

- **`agent(prompt, options)`** — spawn a subagent. Returns the agent's result.
  - `options.model` — model to use (recommended: always set explicitly)
  - `options.label` — display label for the agent
  - `options.phase` — phase name for grouping
  - `options.schema` — JSON schema for structured output
  - `options.agentType` — agent type (default: 'build')
- **`parallel(...fns)`** — run multiple agent calls concurrently
- **`step(name, fn)`** — named phase/step grouping
- **`args`** — global containing input passed to the workflow at invocation

## Saving workflows

Two locations:
- `.claude/workflows/` — project-level, shared via git
- `~/.claude/workflows/` — user-level, all projects

## Behavior & limits

| Constraint | Value |
|---|---|
| Max concurrent agents | 16 (fewer on low-CPU machines) |
| Max agents per run | 1,000 |
| Mid-run user input | Not supported (only permission prompts) |
| FS/shell from script | Not allowed (agents do that) |
| Agent permission mode | Always `acceptEdits`, inherits tool allowlist |
| Resume | Within same session only |

## Passing input

```text
> Run /triage-issues on issues 1024, 1025, and 1030
```
Claude passes structured data as `args`. If omitted, `args` is `undefined`.

## Cost control

- Test on a small slice first (one dir, narrow question)
- `/workflows` shows per-agent token usage live
- Each agent uses session model unless script routes to a different one
- Check `/model` before large runs

## Disable

- `/config` → toggle Dynamic workflows off
- `~/.claude/settings.json` → `"disableWorkflows": true`
- `CLAUDE_CODE_DISABLE_WORKFLOWS=1` env var
- Managed settings for org-wide disable

## Comparison: OpenCode vs Claude Code workflows

| Feature | OpenCode (`opencode-drawer-workflows`) | Claude Code (native) |
|---|---|---|
| Script location | `.agents/workflows/*.workflow.js` | `.claude/workflows/*.js` |
| Primitive: spawn agent | `agent(prompt, opts)` | `agent(prompt, opts)` |
| Primitive: parallel | `parallel(...fns)` | `parallel(...fns)` |
| Primitive: step | `step(name, fn)` | `step(name, fn)` |
| Script metadata | `export const meta = {...}` | Similar but Claude-generated |
| Input | `args` global | `args` global |
| Model default | Plugin-injected, can fail | Session model |
| Save/reuse | Manual file placement | `/workflows` → `s` → save |
| Max agents | Plugin-dependent | 16 concurrent, 1000 total |
| Trigger | `Workflow` tool | `/deep-research`, `ultracode:`, `/effort ultracode` |

### Migration: OpenCode → Claude Code

1. Move `.agents/workflows/*.workflow.js` → `.claude/workflows/*.js`
2. Remove `export const meta = {...}` (Claude Code generates its own metadata)
3. The `agent()`, `parallel()`, `step()`, `args` primitives are compatible
4. Remove hardcoded `model: MODEL` — Claude Code uses session model by default
5. Test via `ultracode: run /workflow-name`

### Migration: Claude Code → OpenCode

1. Move `.claude/workflows/*.js` → `.agents/workflows/*.workflow.js`
2. Add `export const meta = { name, description, phases }` block
3. **MUST** add explicit `model:` to every `agent()` call (OpenCode's default picker is unreliable)
4. Install `opencode-drawer-workflows` plugin
