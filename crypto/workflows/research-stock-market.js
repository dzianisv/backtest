export const meta = {
  name: 'research-stock-market',
  description: 'Portfolio-aware EQUITY research: gather data → consolidate brief → value+macro+systematic panel → chair buy/sell/trim decision → ledger. All substance lives in .agents/skills; this script only orchestrates.',
  phases: [
    { title: 'Gather', detail: 'parallel data seats, each following its own skill' },
    { title: 'Consolidate', detail: 'stock-research-desk skill merges seats into one brief' },
    { title: 'Panel', detail: 'value + macro + systematic lenses + non-voting behavioral guardrail' },
    { title: 'Decide', detail: 'stock-chair skill: portfolio-aware buy/sell/trim decision' },
    { title: 'Ledger', detail: 'log the dated chair call to the forecast-ledger' },
  ],
}

const SKILL = '/Users/engineer/workspace/backtest/.agents/skills'
const LEDGER_PY = `${SKILL}/forecast-ledger/ledger.py`

// Inputs via args (no long text in this script). Date can't come from Date.now() (throws in this runtime).
const REPORT_DATE = (args && args.date) || '2026-06-15'
const QUESTION = (args && args.question) ||
  'NVDA is up ~40% off its April low and I hold 12% of the book in it. I have no AMD or AVGO. Should I trim NVDA or add a cheaper AI-semi name today?'
const PORTFOLIO = (args && args.portfolio) ||
  '~12% of book in NVDA (single-name AI-semi concentration); no other semis; remainder unspecified. Equity risk from risk-capital sleeve only — never the $1.5M house reserve.'
// Optional seed; default '' so Gather fetches LIVE (no stale-number bias).
const ANCHOR = (args && args.anchor) || ''
// Optional ticker hint for the ledger row; chair still drives the call.
const TICKER = (args && args.ticker) || 'EQUITY'

const DATA_SCHEMA = {
  type: 'object',
  properties: {
    seat: { type: 'string' },
    findings: { type: 'array', items: { type: 'object', properties: {
      metric: { type: 'string' }, value: { type: 'string' }, asof: { type: 'string' }, source: { type: 'string' },
    }, required: ['metric', 'value'] } },
    summary: { type: 'string' },
    unavailable: { type: 'array', items: { type: 'string' } },
  },
  required: ['seat', 'findings', 'summary'],
}

const PANEL_SCHEMA = {
  type: 'object',
  properties: {
    seat: { type: 'string' }, read: { type: 'string' },
    verdict: { type: 'string', enum: ['BUY_NOW', 'ADD', 'HOLD', 'TRIM', 'AVOID'] },
    sizing: { type: 'string' }, flip: { type: 'string' },
    confidence: { type: 'string', enum: ['low', 'medium', 'high'] },
  },
  required: ['seat', 'read', 'verdict', 'confidence'],
}

const DECISION_SCHEMA = {
  type: 'object',
  properties: {
    answer: { type: 'string' },
    buy_side: { type: 'string' },
    sell_side: { type: 'string' },
    agreement: { type: 'array', items: { type: 'string' } },
    disagreement: { type: 'array', items: { type: 'string' } },
    verdict_tally: { type: 'string' },
    decision: { type: 'string' },
    sizing_plan: { type: 'string' },
    key_risks: { type: 'array', items: { type: 'string' } },
    invalidation: { type: 'string' },
    confidence: { type: 'string' },
  },
  required: ['answer', 'decision', 'sizing_plan', 'agreement', 'disagreement'],
}

const ctx = `Question: ${QUESTION}\nPortfolio: ${PORTFOLIO}\nAs-of: ${REPORT_DATE}`
const seedNote = ANCHOR ? `\nSeed (verify+extend): ${ANCHOR}` : `\nNo seed — fetch LIVE; never fabricate, mark UNAVAILABLE if gated.`

// ---------- Phase 1: GATHER (data only; each seat follows a skill) ----------
phase('Gather')
const gatherSpecs = [
  { label: 'valuation+quality', skill: 'fundamental-analysis' },
  { label: 'dip-vs-52w', skill: 'dip-screener' },
  { label: 'institutional-13f', skill: 'hedge-fund-13f-analysis' },
  { label: 'congress-buys', skill: 'congressman-stock-watch' },
  { label: 'equity-regime', skill: 'regime-detection' },
  { label: 'technicals', skill: 'analyst-technical-analysis' },
  { label: 'macro-prints', skill: 'fomc-monitor' },
  { label: 'narrative-news', skill: 'narrative-news' },
]
const gatherResults = await parallel(gatherSpecs.map(s => () =>
  agent(`Follow ${SKILL}/${s.skill}/SKILL.md as a DATA-ONLY gather seat (no buy/sell opinion). ${ctx}${seedNote}`,
    { label: s.label, phase: 'Gather', schema: DATA_SCHEMA })
))
// Completeness contract: a missing REQUIRED seat is a defect — never dropped, made LOUD.
const rawData = gatherResults.map((r, i) => (r && r.findings) ? r
  : { seat: gatherSpecs[i].label, status: 'UNAVAILABLE', findings: [], summary: `[UNAVAILABLE: ${gatherSpecs[i].label} seat failed to return]` })
const missingSeats = rawData.filter(r => r.status === 'UNAVAILABLE').map(r => r.seat)
const gatherComplete = missingSeats.length === 0
if (!gatherComplete) log(`WARNING: INCOMPLETE GATHER — UNAVAILABLE: ${missingSeats.join(', ')} (run not aborted; gap surfaced).`)
log(`Gather: ${rawData.length - missingSeats.length}/${gatherSpecs.length} seats returned`)

// ---------- Phase 2: CONSOLIDATE (stock-research-desk skill) ----------
phase('Consolidate')
const completeNote = gatherComplete ? 'All categories returned.' : `INCOMPLETE — [UNAVAILABLE]: ${missingSeats.join(', ')}. Surface as DATA GAPS; do not paper over.`
const brief = await agent(
  `Follow ${SKILL}/stock-research-desk/SKILL.md. ${ctx}\nCompleteness: ${completeNote}\nRAW DATA:\n${JSON.stringify(rawData, null, 1)}`,
  { label: 'consolidate', phase: 'Consolidate' })

// ---------- Phase 3: PANEL (each lens follows its skill, reasons over the brief) ----------
phase('Panel')
const lenses = [
  { seat: 'Warren Buffett', skill: 'analytics-warren-buffett' },
  { seat: 'Benjamin Graham', skill: 'analytics-benjamin-graham' },
  { seat: 'Druckenmiller', skill: 'analytics-stanley-druckenmiller' },
  { seat: 'Lyn Alden (macro)', skill: 'analytics-lyn-alden' },
  { seat: 'systematic-trading', skill: 'analyst-systematic-trading' },
  { seat: 'Lacy Hunt (dissent)', skill: 'analytics-lacy-hunt' },
]
const verdicts = (await parallel(lenses.map(l => () =>
  agent(`Apply the lens in ${SKILL}/${l.skill}/SKILL.md to answer the question, reasoning ONLY over the brief (don't re-fetch). ${ctx}\nReturn seat, read, verdict (BUY_NOW/ADD/HOLD/TRIM/AVOID) for the question, sizing, flip-condition, confidence.\n=== BRIEF ===\n${brief}`,
    { label: l.seat, phase: 'Panel', schema: PANEL_SCHEMA })
))).map((r, i) => r || { seat: lenses[i].seat, read: '[UNAVAILABLE: seat failed]', verdict: 'HOLD', confidence: 'low' })
log(`Panel: ${verdicts.filter(v => v.read.indexOf('[UNAVAILABLE') === -1).length}/${lenses.length} seats voted`)

// Housel = NON-VOTING behavioral guardrail (process + sizing only).
const guardrail = await agent(
  `Follow ${SKILL}/analytics-morgan-housel/SKILL.md as a NON-VOTING guardrail (no BUY/SELL verdict). ${ctx}\nAssess: FOMO-vs-anchoring trap on a winner up big, is a scale-in/trim sound, is single-name sizing survivable to a thesis-break drawdown, one guardrail rule. Reason over the brief.\n=== BRIEF ===\n${brief}`,
  { label: 'Housel (guardrail)', phase: 'Panel' })

// ---------- Phase 4: DECIDE (stock-chair skill — portfolio-aware buy/sell/trim) ----------
phase('Decide')
const decision = await agent(
  `Follow ${SKILL}/stock-chair/SKILL.md to chair the committee and answer the question for THIS portfolio. ${ctx}\n` +
  `=== BRIEF ===\n${brief}\n=== VOTING VERDICTS ===\n${JSON.stringify(verdicts, null, 1)}\n=== HOUSEL GUARDRAIL (non-voting) ===\n${guardrail}`,
  { label: 'chair-decision', phase: 'Decide', schema: DECISION_SCHEMA })

// ---------- Phase 5: WRITE REPORT ----------
const reportPath = `/Users/engineer/workspace/backtest/research/research.stock.${REPORT_DATE}.md`
const seatRows = verdicts.map(v => `| ${v.seat} | **${v.verdict}** | ${v.confidence} |`).join('\n')
const seatDetail = verdicts.map(v => `### ${v.seat} — ${v.verdict} (${v.confidence})\n${v.read}\n\n- **Sizing:** ${v.sizing || 'n/a'}\n- **Flips if:** ${v.flip || 'n/a'}`).join('\n\n')
const reportMd = `# Stock Research — ${REPORT_DATE}

> Question: ${QUESTION}
> Portfolio: ${PORTFOLIO}
> Generated by \`research-stock-market\`. Educational, not advice; re-pull before acting.
${gatherComplete ? '' : `\n> **⚠ INCOMPLETE DATA:** UNAVAILABLE seats: ${missingSeats.join(', ')}. Treat with caution.\n`}
## Answer
**${decision.answer || decision.decision}**

## Decision
${decision.decision}

**Buy-side:** ${decision.buy_side || 'n/a'}
**Sell/trim-side:** ${decision.sell_side || 'n/a'}
**Sizing plan:** ${decision.sizing_plan}
**Verdict tally:** ${decision.verdict_tally || 'see table'}
**Invalidation:** ${decision.invalidation || 'n/a'}

### Agreement
${(decision.agreement || []).map(a => `- ${a}`).join('\n')}
### Disagreement (preserved)
${(decision.disagreement || []).map(d => `- ${d}`).join('\n')}
### Key risks
${(decision.key_risks || []).map(r => `- ${r}`).join('\n')}

## Panel votes
| Seat | Verdict | Confidence |
|---|---|---|
${seatRows}

## Seat detail
${seatDetail}

## Behavioral guardrail (Housel — non-voting)
${guardrail}

## Consolidated brief (evidence)
${brief}
`
await agent(`Use the Write tool to create EXACTLY this file:\n${reportPath}\nWrite this content VERBATIM (no edits/summary). Create parent dirs. Reply with just the path.\n--- BEGIN ---\n${reportMd}\n--- END ---`,
  { label: 'write-report', phase: 'Decide' })
log(`Report written: ${reportPath}`)

// ---------- Phase 6: LEDGER ----------
phase('Ledger')
const bull = ['BUY_NOW', 'ADD']
const votes = verdicts.filter(v => v && v.verdict && v.read.indexOf('[UNAVAILABLE') === -1)
const bullCount = votes.filter(v => bull.indexOf(v.verdict) !== -1).length
const impliedProb = votes.length ? (bullCount / votes.length) : 0.5
const horizon = REPORT_DATE.slice(0, 4) + '-12-31'
const votingLenses = votes.map(v => v.seat).join(', ') || 'stock-panel'
const ledgerLog = await agent(
  `Use Bash to run EXACTLY (appends one dated forecast row):\n\n` +
  `python3 ${LEDGER_PY} add --asset ${JSON.stringify(TICKER)} --q ${JSON.stringify('stock-panel chair call: ' + (decision.answer || decision.decision || '(none)'))} ` +
  `--p ${impliedProb.toFixed(2)} --by ${JSON.stringify(horizon)} --lens ${JSON.stringify(votingLenses)} ` +
  `--source research-stock-market --flip ${JSON.stringify(decision.invalidation || 'n/a')} --created ${JSON.stringify(REPORT_DATE)}\n\n` +
  `--p is derived from the voting tally (${bullCount}/${votes.length} add/buy) — do not change it. If "id exists", re-run once with --id ${TICKER.toLowerCase()}-${REPORT_DATE}-panel. Reply with the CLI's stdout line.`,
  { label: 'ledger-log', phase: 'Ledger' })
log(`Ledger: ${ledgerLog}`)

return { reportPath, decision, verdicts, guardrail, brief, complete: gatherComplete, missing: missingSeats,
  ledger: { impliedProb, horizon, lenses: votingLenses, result: ledgerLog } }
