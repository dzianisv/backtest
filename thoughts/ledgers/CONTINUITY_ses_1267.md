---
session: ses_1267
updated: 2026-06-18T07:04:06.951Z
---

# Session Summary

## Goal
Understand the full evaluation infrastructure and patterns used in the backtest repo — read all eval harnesses, eval skills, the skill-supervisor loop, and the research-market workflow to map out how skills are tested and improved.

## Constraints & Preferences
- Return FULL CONTENT of each file (user wants to understand patterns, not just summaries)
- Check for 13f-watch or filing-related evals specifically
- No files modified — read-only exploration

## Progress
### Done
- [x] Listed `evals/` directory structure: three subdirs `crypto/`, `hf/`, `pm/`
- [x] Read all three eval SKILL.md files: `hedge-fund-committee-eval`, `crypto-workflow-eval`, `skill-supervisor`
- [x] Read all `evals/pm/` files: `evaluate.py`, `gen_scenarios.py`, `score_decision.py`, `JUDGE_RUBRIC.md`, `RESULTS.md`, `scenarios/inputs.jsonl`, `scenarios/scenarios.jsonl`
- [x] Read all `evals/hf/` files: `evaluate_hf.py`, `score_capability.py`, `apply_score_caps.mjs`, `test_gate_contract.mjs`, `JUDGE_RUBRIC.md`, `RESULTS.md`
- [x] Read all `evals/crypto/` files: `run_crypto_eval.py`, `JUDGE_RUBRIC.md`, `README.md`, `RESULTS.md`
- [x] Read `.agents/workflows/research-market.workflow.js`
- [x] Confirmed NO 13f-watch or filing-related evals exist in `evals/` (grep returned no matches for "13f")

### In Progress
- [ ] (none — all requested reads complete)

### Blocked
- (none)

## Key Decisions
- **Supervisor/executor separation is the core anti-reward-hack pattern**: The role that changes the prompt is never the role that scores it. Single-agent self-reflection + self-modification = DGM/Hyperagents failure mode. All three eval domains enforce this.
- **Deterministic + qualitative split**: Every eval separates machine-checkable scoring (regime, dip tiers, section coverage) from LLM-judge qualitative scoring. The judge never sees the weights → can't game the total.
- **Invariant gates zero the score**: `places_trades`, `fabricated_holdings`, `reckless_advice` → instant 0 across all harnesses.

## Next Steps
1. User now has full content of all eval files — awaiting further instructions on what to build, modify, or analyze
2. Potential follow-up: create a 13f-watch eval harness (none exists yet)
3. Potential follow-up: analyze the `evals/crypto/answers/` and `evals/crypto/judgements/` individual files (not yet read)
4. Potential follow-up: read `evals/hf/scenarios/scenarios.jsonl` and `evals/hf/scenarios/inputs.jsonl` (not yet read)

## Critical Context
- **Three eval domains exist**: `pm/` (tradfi portfolio manager), `hf/` (hedge-fund-manager ops reports), `crypto/` (crypto advisor G-Eval)
- **PM eval** (`evals/pm/`): 10 historical S&P scenarios (7 train / 3 holdout), deterministic ground truth from yfinance (regime from 200d MA, dip tiers from drawdown, rebalance from quarter-end). Score: regime 25 + dip_tiers 35 + rebalance 15 + judge_qualitative 25 = 100. Reached **100/100 train+holdout at v3** via supervisor/executor architecture.
- **HF eval** (`evals/hf/`): 6 fund-state scenarios (4 train / 2 holdout). Score: coverage 40 (parsed `<section>` tags) + cadence 15 + decision calls 25 + backtest gate 5 + judge 15 = 100. `apply_score_caps.mjs` enforces hard caps: FLAGSHIP_EXCLUSION → ceiling 35, ALL_PASS → ceiling 45. `test_gate_contract.mjs` regression-tests the SanDisk narrative-name discovery gate. Reached **99.2 train / 99.0 holdout at v1** (team delegation).
- **Crypto eval** (`evals/crypto/`): 6 scenarios (3 train / 3 holdout), G-Eval style (Liu et al. 2023) — CoT then form-fill 1–5. Weights: grounding 20 + framework 20 + risk 25 + honesty 20 + actionability 15 = 100. Judge is blind to weights. Baseline **85.0 overall**. Fine-tune gaps: no explicit "no leverage", vague sizing, missing disclaimer on one holdout.
- **skill-supervisor** (`skill-supervisor/SKILL.md`): Drives run→score→fix→rerun loop with three hard-separated roles: Supervisor (scores, selects, never edits SKILL.md), Runner (executes skill blind to rubric), Editor (applies diffs blind to scores). Prevents reward-hacking. Uses `propose/dispose` pattern.
- **research-market.workflow.js**: Unified portfolio-aware workflow. An LLM MANAGER discovers skills live (no hardcoded roster), decides assets/seats/feeds/panel/desk/chair. Phases: Intake → Gather (parallel data seats) → Consolidate → Panel (multi-lens debate + behavioral guardrail) → Decide (chair) → Ledger. Uses `claude-sonnet-4` model. Skill path: `/Users/engineer/workspace/backtest/.agents/skills`. Workflow exists at three locations: `.agents/workflows/`, `.opencode/workflows/`, `.claude/workflows/`.

## File Operations
### Read
- `/Users/engineer/workspace/backtest/.agents/skills/crypto-workflow-eval/SKILL.md`
- `/Users/engineer/workspace/backtest/.agents/skills/hedge-fund-committee-eval/SKILL.md`
- `/Users/engineer/workspace/backtest/.agents/skills/skill-supervisor/SKILL.md`
- `/Users/engineer/workspace/backtest/.agents/workflows/research-market.workflow.js`
- `/Users/engineer/workspace/backtest/evals` (directory listing)
- `/Users/engineer/workspace/backtest/evals/crypto/JUDGE_RUBRIC.md`
- `/Users/engineer/workspace/backtest/evals/crypto/README.md`
- `/Users/engineer/workspace/backtest/evals/crypto/RESULTS.md`
- `/Users/engineer/workspace/backtest/evals/crypto/run_crypto_eval.py`
- `/Users/engineer/workspace/backtest/evals/hf/JUDGE_RUBRIC.md`
- `/Users/engineer/workspace/backtest/evals/hf/RESULTS.md`
- `/Users/engineer/workspace/backtest/evals/hf/apply_score_caps.mjs`
- `/Users/engineer/workspace/backtest/evals/hf/evaluate_hf.py`
- `/Users/engineer/workspace/backtest/evals/hf/score_capability.py`
- `/Users/engineer/workspace/backtest/evals/hf/test_gate_contract.mjs`
- `/Users/engineer/workspace/backtest/evals/pm/JUDGE_RUBRIC.md`
- `/Users/engineer/workspace/backtest/evals/pm/RESULTS.md`
- `/Users/engineer/workspace/backtest/evals/pm/evaluate.py`
- `/Users/engineer/workspace/backtest/evals/pm/gen_scenarios.py`
- `/Users/engineer/workspace/backtest/evals/pm/scenarios/inputs.jsonl`
- `/Users/engineer/workspace/backtest/evals/pm/scenarios/scenarios.jsonl`
- `/Users/engineer/workspace/backtest/evals/pm/score_decision.py`

### Modified
- (none)
