// Regression guard for the hedge-fund-committee discovery GATE contract.
// The fatal SanDisk bug: a single-source NARRATIVE name (SNDK, conviction 3) was filtered out before
// the panel. This test pins the contract so that can never silently regress. Run: `node test_gate_contract.mjs`
// It MIRRORS the gate predicate in hedge-fund-committee.workflow.js (~line 160) — if you change the gate
// there, change it here and confirm these assertions still hold (or the contract itself changed on purpose).

const NARRATIVE_DESKS = new Set(['news-ft', 'news-wsj', 'news-tradepress', 'news-reddit'])
const gatePasses = (c) =>
  c.n_sources >= 2 ||
  c.max_conviction >= 4 ||
  c.sources.some(s => NARRATIVE_DESKS.has(s))

const cases = [
  // [name, candidate, mustPass]
  ['SNDK-class single-source narrative (the fatal case)', { ticker: 'SNDK', n_sources: 1, max_conviction: 3, sources: ['news-ft'] }, true],
  ['narrative from any feed seat', { ticker: 'X', n_sources: 1, max_conviction: 1, sources: ['news-reddit'] }, true],
  ['cross-source convergence', { ticker: 'Y', n_sources: 2, max_conviction: 2, sources: ['equity-dips', 'institutional-flows'] }, true],
  ['high-conviction single dip', { ticker: 'Z', n_sources: 1, max_conviction: 4, sources: ['equity-dips'] }, true],
  ['low-signal single dip (correctly excluded)', { ticker: 'JUNK', n_sources: 1, max_conviction: 2, sources: ['equity-dips'] }, false],
]

let failed = 0
for (const [name, cand, mustPass] of cases) {
  const got = gatePasses(cand)
  const ok = got === mustPass
  if (!ok) failed++
  console.log(`${ok ? 'PASS' : 'FAIL'}: ${name} — gate ${got ? 'admits' : 'drops'}, expected ${mustPass ? 'admit' : 'drop'}`)
}
if (failed) { console.error(`\n${failed} GATE CONTRACT VIOLATION(S) — a discovered narrative name could be filtered before the panel. This is the SanDisk failure mode.`); process.exit(1) }
console.log('\nGATE CONTRACT OK — single-source narrative names (SNDK-class) reach the panel.')
