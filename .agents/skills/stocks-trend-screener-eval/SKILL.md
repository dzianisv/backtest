---
name: stocks-trend-screener-eval
description: "Evaluates one run of the stocks-trend-screener skill against the RUBRIC. Spawns an actor subagent to run the screener, then spawns an independent judge subagent (blind) to score the output across 6 rubric dimensions. Appends one row to .agents/skills/stocks-trend-screener/eval.csv. Triggers: 'eval the screener', 'score the screener run', 'run eval on stocks-trend-screener'."
license: MIT
compatibility: opencode
---

# Stocks-Trend-Screener Evaluator

Evaluate one run of the `stocks-trend-screener` skill by running an actor then scoring with a blind judge. Append results to `eval.csv`.

## Role
You are an evaluation orchestrator. Your job is to run the screener, get a result, score it against the rubric, and record the score. You do NOT judge the output yourself — you delegate scoring to an independent subagent.

## Rubric file
`.agents/skills/stocks-trend-screener/evals/RUBRIC.md` — 6 dimensions, 0–5 each:
1. `source_grounding` — did it read real journalism, or hallucinate/speculate?
2. `non_obvious_discovery` — did it map past the obvious leader to a hidden beneficiary?
3. `skeptic_discipline` — did it kill candidates that fail (already priced, no catalyst, no named risk)?
4. `actionability` — are finalists concrete enough for multi-lens-quorum to judge?
5. `quorum_routing` — did it route to quorum, not self-decide buy/sell?
6. `prescreen_usage` — did it use the quantitative scanner as Step 1 to direct reading?

## Eval cases
- Train cases: `.agents/skills/stocks-trend-screener/evals/cases/train/`
- Holdout case: `.agents/skills/stocks-trend-screener/evals/cases/holdout/`

## Step 1 — Pick eval case

Default: use train case `02-weekly-scan.md` (RESEARCH_MODE).
If user specifies a case file, use that instead.

Read the case file to get the input prompt, expected mode, and which dimensions apply (`applies:` frontmatter).

## Step 2 — Run actor (isolated subagent)

Spawn a subagent with the stocks-trend-screener skill instructions + the eval case input prompt:

```
Invoke the stocks-trend-screener skill.
Input: [case input prompt from step 1]
Run the skill fully — all steps. Produce the final output.
```

Wait for the actor to complete. Capture the full output.

## Step 3 — Run judge (blind, independent subagent)

Spawn a SEPARATE subagent that has:
1. The actor's output (but NOT the actor's instructions/skill body — blind scoring)
2. The RUBRIC.md content
3. This scoring prompt:

```
You are a blind evaluator. Score the following screener output against the rubric.
Do NOT read the skill's instructions — score ONLY what the output actually contains.

RUBRIC:
[paste RUBRIC.md content here]

APPLICABLE DIMENSIONS for this case: [dimensions from case frontmatter]

OUTPUT TO SCORE:
[paste actor output here]

For each applicable dimension, provide:
- Score: 0–5
- One-sentence justification (what you saw or did not see)

Then provide:
- Overall mean score (across applicable dimensions only)
- Top improvement suggestion (single sentence — what to fix to raise the score most)

Format:
source_grounding: N — [justification]
non_obvious_discovery: N — [justification]
skeptic_discipline: N — [justification]
actionability: N — [justification]
quorum_routing: N — [justification]
prescreen_usage: N — [justification]
MEAN: N.NN
SUGGESTION: [one sentence]
```

Wait for judge to complete. Extract scores.

## Step 4 — Append to eval.csv

Get current git commit:
```bash
COMMIT=$(cd /Users/engineer/workspace/backtest && git rev-parse --short HEAD)
```

Append one row to `.agents/skills/stocks-trend-screener/eval.csv`:
```
{commit_id},{eval_input_prompt},{score},{judge_feedback},{suggestions}
```

Where:
- `commit_id` = current HEAD short SHA
- `eval_input_prompt` = the input prompt from the case (escaped for CSV — wrap in quotes, double-escape inner quotes)
- `score` = `"N.NN (source_grounding=N non_obvious=N skeptic=N actionability=N quorum_routing=N prescreen=N)"` — the formatted string from judge
- `judge_feedback` = the judge's per-dimension justifications, concatenated
- `suggestions` = the judge's single improvement suggestion

```python
import csv, subprocess, datetime, os

commit = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'],
                                  cwd='/Users/engineer/workspace/backtest').decode().strip()

row = {
    'commit_id': commit,
    'eval_input_prompt': eval_input_prompt,  # from case
    'score': score_string,
    'judge_feedback': judge_feedback_string,
    'suggestions': suggestion_string,
}

csv_path = '.agents/skills/stocks-trend-screener/eval.csv'
file_exists = os.path.exists(csv_path)
with open(csv_path, 'a', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['commit_id','eval_input_prompt','score','judge_feedback','suggestions'])
    if not file_exists:
        w.writeheader()
    w.writerow(row)
print(f"Appended eval row to {csv_path}")
```

## Step 5 — Print summary

Print:
```
EVAL COMPLETE — stocks-trend-screener
Commit: {commit}
Case: {case_file}
Score: {mean} ({per-dim breakdown})
Feedback: {top suggestion}
CSV: .agents/skills/stocks-trend-screener/eval.csv (row appended)
```

## Done when
- Actor ran to completion
- Judge scored each applicable dimension
- One row appended to eval.csv
- Summary printed
