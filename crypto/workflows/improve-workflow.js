// NOTE (superseded): this self-contained loop is BLOCKED — workflow() cannot nest a heavy target here.
// Use the ORCHESTRATED procedure in crypto/eval/IMPROVE-LOOP.md with pairwise-eval.js for selection.
// improve-workflow.js — ONE round of a Reflexion + DSPy-style instruction-optimization loop.
//
// MEASUREMENT-AND-IMPROVEMENT ARE SEPARATED; a human gate is recommended before merging
// accepted edits. Judges are BLIND — they see only a run's output (brief + decision), never
// the workflow code, the rubric author, the proposer, or any prior score. This addresses the
// self-grading reward-hack where a prior self-graded loop inflated its own scores.
//
// Roles are strictly partitioned so no agent grades its own work:
//   JUDGE  (3x, blind)  -> measures.   never proposes or edits.
//   REFLECTOR           -> diagnoses the single weakest module from blind gap reports.
//   PROPOSER            -> proposes K candidate instruction rewrites.   never judges or edits.
//   EXECUTOR            -> applies one candidate, re-evals via the SAME blind judges, reverts.
// PROPOSER != JUDGE != EXECUTOR.
//
// Args:
//   args.target    -> 'research-crypto-market' | 'research-stock-market'
//   args.holdout   -> [{ question, portfolio, ticker? }, ...] frozen eval cases
//   args.skillsDir -> default /Users/engineer/workspace/backtest/.agents/skills
//   args.date      -> as-of date passed to the target workflow (no Date.now in this runtime)
//   args.k         -> # of candidate rewrites (default 3)

export const meta = {
  name: 'improve-workflow',
  description: 'One round of a blind-judged Reflexion + DSPy-style instruction-optimization loop over a research workflow. Strict propose/dispose (judge != proposer != executor) to defeat self-grading reward-hacks. Returns the round summary; human gate recommended before merge.',
  phases: [
    { title: 'Eval', detail: 'run target on holdout; 3 BLIND judges score each run (evidence-weighted)' },
    { title: 'Reflexion', detail: 'one reflector names the single weakest module from blind gaps' },
    { title: 'Optimize', detail: 'proposer drafts K instruction rewrites of that one skill' },
    { title: 'Dispose', detail: 'executor applies each candidate, re-evals blind, keeps best IFF > baseline' },
    { title: 'Commit', detail: 'commit the winning edit with the blind score delta; else revert all' },
  ],
}

const SKILLS_DIR = (args && args.skillsDir) || '/Users/engineer/workspace/backtest/.agents/skills'
const TARGET = (args && args.target) || 'research-crypto-market'
// Invoke the target by FILE, not by name: research-*.js are committed scripts, not registered saved
// workflows, so workflow(NAME) resolves to null and the target never runs (baseline scored 0). scriptPath is reliable.
const TARGET_PATH = (args && args.targetPath) || `/Users/engineer/workspace/backtest/crypto/workflows/${TARGET}.js`
const DATE = (args && args.date) || '2026-06-15'
const K = (args && args.k) || 3
const HOLDOUT = (args && args.holdout) || []
if (!HOLDOUT.length) log('WARNING: empty holdout — eval will be vacuous. Pass args.holdout=[{question,portfolio}].')

// INDEPENDENT score schema. Evidence/grounding is weighted >= 50% on purpose; the judge never
// sees the rubric author or the workflow internals, only the run output.
const JUDGE_SCHEMA = {
  type: 'object',
  properties: {
    evidence_grounding: { type: 'number' },   // 0-50  (>=50% of total weight)
    answers_question:   { type: 'number' },    // 0-20
    portfolio_aware:    { type: 'number' },    // 0-15
    disagreement_kept:  { type: 'number' },    // 0-10
    discipline:         { type: 'number' },    // 0-5
    total:              { type: 'number' },     // 0-100 = sum of the above
    module_gaps: { type: 'array', items: { type: 'object', properties: {
      module: { type: 'string' }, gap: { type: 'string' },
    }, required: ['module', 'gap'] } },
  },
  required: ['evidence_grounding', 'answers_question', 'portfolio_aware', 'total', 'module_gaps'],
}

const JUDGE_RUBRIC =
  `You are a BLIND, independent grader. You see ONLY the run output below — never the code that ` +
  `produced it, never who wrote this rubric, never any prior or other judge's score. Score 0-100 ` +
  `on this INDEPENDENT schema (evidence is >= half the weight ON PURPOSE):\n` +
  `- evidence_grounding 0-50: every material claim sourced + dated; priced/live data not paraphrased ` +
  `from a digest; NO fabricated numbers. This is the dominant axis — a fluent but ungrounded answer scores LOW.\n` +
  `- answers_question 0-20: direct yes/no/partial to exactly what was asked, up front.\n` +
  `- portfolio_aware 0-15: maps holdings to real exposure; recommends BOTH a buy-side and a sell/trim-side.\n` +
  `- disagreement_kept 0-10: bear dissent preserved, not averaged into mush.\n` +
  `- discipline 0-5: concrete sizing/tranche + invalidation; survivable sizing; no leverage; no overclaiming.\n` +
  `total = the sum. Also return module_gaps: for each weak area, name the MODULE (a seat/skill role ` +
  `like 'valuation+quality', 'narrative-news', 'chair', 'research-desk') and the specific gap. ` +
  `Be harsh and specific. Do not reward length.`

// Median of an odd/even list; drop the single furthest outlier before median when >=3 judges.
function aggregate(scores) {
  const vals = scores.map(s => (s && typeof s.total === 'number') ? s.total : 0)
  let kept = vals.slice()
  if (kept.length >= 3) {
    const mean = kept.reduce((a, b) => a + b, 0) / kept.length
    let worstI = 0, worstD = -1
    kept.forEach((v, i) => { const d = Math.abs(v - mean); if (d > worstD) { worstD = d; worstI = i } })
    kept = kept.filter((_, i) => i !== worstI)   // drop furthest outlier
  }
  const sorted = kept.slice().sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  const median = sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2
  return median
}

// Run the target on the whole holdout and blind-judge each run. Returns {meanMedian, perCaseGaps[]}.
async function evalHoldout(label) {
  const caseResults = await pipeline(HOLDOUT, async (q) => {
    const run = await workflow({ scriptPath: TARGET_PATH }, { question: q.question, portfolio: q.portfolio, ticker: q.ticker, date: DATE })
    if (!run || !run.decision) {  // loud, not a silent 0 — a non-running target must be visible, not scored
      log(`ERROR [${label}]: target ${TARGET_PATH} returned no decision — eval is INVALID for this case, not a real 0.`)
      return { caseMedian: null, gaps: [{ module: 'TARGET', gap: 'target workflow returned no decision (did not run)' }], invalid: true }
    }
    // Judges see ONLY the run's product — brief + decision + votes. Never the code.
    const runView =
      `=== DECISION ===\n${JSON.stringify(run && run.decision, null, 1)}\n` +
      `=== PANEL VOTES ===\n${JSON.stringify(run && run.verdicts, null, 1)}\n` +
      `=== BRIEF (evidence) ===\n${run && run.brief}`
    const judgePrompt = `${JUDGE_RUBRIC}\n\nQUESTION ASKED: ${q.question}\nPORTFOLIO: ${q.portfolio}\n\n=== RUN OUTPUT (all you may see) ===\n${runView}`
    const judges = await parallel([0, 1, 2].map(j => () =>
      agent(judgePrompt, { label: `${label}-judge${j}`, phase: 'Eval', schema: JUDGE_SCHEMA })
    ))
    const valid = judges.filter(Boolean)
    return { caseMedian: aggregate(valid), gaps: valid.flatMap(s => (s && s.module_gaps) || []) }
  })
  const validCases = caseResults.filter(c => c && c.caseMedian != null)  // exclude non-running targets
  const meanMedian = validCases.length
    ? validCases.reduce((a, c) => a + c.caseMedian, 0) / validCases.length : null
  const perCaseGaps = caseResults.map((c, i) => ({ case: i, median: c && c.caseMedian, gaps: (c && c.gaps) || [] }))
  return { meanMedian, perCaseGaps, invalid: validCases.length === 0 }
}

// ---------- Phase 1: EVAL (baseline measurement) ----------
phase('Eval')
const baseline = await evalHoldout('baseline')
if (baseline.invalid || baseline.meanMedian == null) {  // target never ran — abort loudly, do NOT proceed on a fake 0
  log(`ABORT: baseline eval invalid — target ${TARGET_PATH} produced no scorable runs. Fix the target invocation before optimizing.`)
  return { round_summary: `ABORT: target did not run (no scorable baseline). Check ${TARGET_PATH}.`,
    target: TARGET, weakest_module: null, baseline_score: null, best_candidate_score: null, accepted: false, commit: null, invalid: true }
}
log(`Baseline blind score (mean of per-case medians): ${baseline.meanMedian.toFixed(1)}`)

// ---------- Phase 2: REFLEXION (diagnose the SINGLE weakest module) ----------
phase('Reflexion')
const reflection = await agent(
  `You are the REFLECTOR. Read the aggregated BLIND gap reports across all holdout cases below. ` +
  `Name the SINGLE weakest MODULE (one skill) and WHY, as concrete verbal feedback the proposer can act on. ` +
  `Pick exactly one. Return JSON {weakest_module, why}. The module name MUST be a skill that exists under ` +
  `${SKILLS_DIR} (e.g. a gather seat, the research-desk, a panel lens, or the chair).\n\n` +
  `=== BLIND GAP REPORTS ===\n${JSON.stringify(baseline.perCaseGaps, null, 1)}`,
  { label: 'reflector', phase: 'Reflexion',
    schema: { type: 'object', properties: { weakest_module: { type: 'string' }, why: { type: 'string' } }, required: ['weakest_module', 'why'] } })
const weakestModule = (reflection && reflection.weakest_module || '').trim()
log(`Reflector named weakest module: ${weakestModule}`)

// Resolve the skill file. If the named module isn't a real skill dir, abort this round cleanly.
const skillPath = `${SKILLS_DIR}/${weakestModule}/SKILL.md`
const exists = await agent(
  `Use Bash: test -f ${JSON.stringify(skillPath)} && echo EXISTS || echo MISSING. Reply with exactly EXISTS or MISSING.`,
  { label: 'resolve-skill', phase: 'Reflexion' })
if (!exists || exists.indexOf('EXISTS') === -1) {
  log(`ABORT round: weakest_module '${weakestModule}' did not resolve to ${skillPath}.`)
  return { round_summary: `no-op: reflector named non-existent module '${weakestModule}'`, target: TARGET,
    weakest_module: weakestModule, baseline_score: baseline.meanMedian, best_candidate_score: baseline.meanMedian,
    accepted: false, commit: null }
}

// ---------- Phase 3: DSPy-style OPTIMIZE (PROPOSER drafts K instruction rewrites) ----------
phase('Optimize')
const currentSkill = await agent(
  `Use the Read tool on ${skillPath} and reply with its FULL verbatim contents only.`,
  { label: 'read-skill', phase: 'Optimize' })
const proposal = await agent(
  `You are the PROPOSER (NOT a judge, NOT the executor). Here is the current SKILL.md and the reflector's ` +
  `feedback on why this module is the weakest. Propose ${K} candidate INSTRUCTION REWRITES of this skill ` +
  `(instruction-optimization — sharpen the directives/contract; do NOT add few-shot demos or fabricated examples). ` +
  `Each candidate must be a COMPLETE drop-in SKILL.md (keep the YAML frontmatter name identical). ` +
  `Make them genuinely different bets on fixing the gap.\n\n` +
  `=== REFLECTION ===\n${JSON.stringify(reflection, null, 1)}\n\n=== CURRENT SKILL.md ===\n${currentSkill}`,
  { label: 'proposer', phase: 'Optimize',
    schema: { type: 'object', properties: { candidates: { type: 'array', items: { type: 'object', properties: {
      rationale: { type: 'string' }, skill_md: { type: 'string' },
    }, required: ['skill_md'] } } }, required: ['candidates'] } })
const candidates = ((proposal && proposal.candidates) || []).slice(0, K)
log(`Proposer returned ${candidates.length} candidate rewrite(s) for ${weakestModule}`)

// ---------- Phase 4: DISPOSE / SELECT (EXECUTOR applies, re-evals BLIND, isolates via git) ----------
phase('Dispose')
let best = { idx: -1, score: baseline.meanMedian, skill_md: null }
for (let i = 0; i < candidates.length; i++) {
  const cand = candidates[i]
  // Isolate: stash any working changes, write candidate, eval, then hard-restore the file.
  await agent(
    `Use Bash. Run, in order, reporting the final stdout:\n` +
    `git -C /Users/engineer/workspace/backtest stash push -- ${JSON.stringify(skillPath)} 2>/dev/null || true\n` +
    `Then use the Write tool to overwrite ${skillPath} with EXACTLY this content (verbatim):\n` +
    `--- BEGIN ---\n${cand.skill_md}\n--- END ---\nReply 'WROTE'.`,
    { label: `exec-write-${i}`, phase: 'Dispose' })
  const trial = await evalHoldout(`cand${i}`)
  log(`Candidate ${i} blind score: ${trial.meanMedian.toFixed(1)} (baseline ${baseline.meanMedian.toFixed(1)})`)
  // Restore the skill to its committed state before trying the next candidate.
  await agent(
    `Use Bash: git -C /Users/engineer/workspace/backtest checkout -- ${JSON.stringify(skillPath)} && ` +
    `git -C /Users/engineer/workspace/backtest stash list | grep -q . && git -C /Users/engineer/workspace/backtest stash drop 2>/dev/null; echo RESTORED. Reply RESTORED.`,
    { label: `exec-restore-${i}`, phase: 'Dispose' })
  if (trial.meanMedian > best.score) best = { idx: i, score: trial.meanMedian, skill_md: cand.skill_md }
}

// ---------- Phase 5: COMMIT (winning edit IFF it beats baseline; else revert all) ----------
phase('Commit')
let accepted = false, commit = null
if (best.idx >= 0 && best.score > baseline.meanMedian) {
  const delta = (best.score - baseline.meanMedian).toFixed(1)
  const msg = `improve(${weakestModule}): blind-judged instruction rewrite +${delta} (${baseline.meanMedian.toFixed(1)}→${best.score.toFixed(1)}) on ${TARGET}\n\n` +
    `Candidate #${best.idx} won a blind re-eval on the frozen holdout (judges != proposer != executor).\n` +
    `HUMAN GATE recommended before merge.\n\n` +
    `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
  commit = await agent(
    `Use Bash. Apply the winning candidate and commit ONLY this one skill file:\n` +
    `Use the Write tool to overwrite ${skillPath} with EXACTLY (verbatim):\n--- BEGIN ---\n${best.skill_md}\n--- END ---\n` +
    `Then: git -C /Users/engineer/workspace/backtest add ${JSON.stringify(skillPath)} && ` +
    `git -C /Users/engineer/workspace/backtest commit -m ${JSON.stringify(msg)} && ` +
    `git -C /Users/engineer/workspace/backtest rev-parse --short HEAD\n` +
    `Reply with just the commit hash.`,
    { label: 'commit-winner', phase: 'Commit' })
  accepted = true
  log(`ACCEPTED candidate ${best.idx}: +${delta} → committed ${commit} (human gate recommended).`)
} else {
  // Belt-and-suspenders: ensure the file is at its committed state.
  await agent(
    `Use Bash: git -C /Users/engineer/workspace/backtest checkout -- ${JSON.stringify(skillPath)}; echo REVERTED. Reply REVERTED.`,
    { label: 'revert-all', phase: 'Commit' })
  log(`No candidate beat baseline (${baseline.meanMedian.toFixed(1)}); reverted all. Nothing committed.`)
}

return {
  round_summary: accepted
    ? `Accepted blind-judged rewrite of ${weakestModule} on ${TARGET}: ${baseline.meanMedian.toFixed(1)}→${best.score.toFixed(1)}`
    : `No improvement this round on ${TARGET}; weakest=${weakestModule}; baseline held at ${baseline.meanMedian.toFixed(1)}`,
  target: TARGET,
  weakest_module: weakestModule,
  baseline_score: baseline.meanMedian,
  best_candidate_score: best.score,
  accepted,
  commit,
}
