/**
 * citation-validator.ts — OpenCode plugin
 * Hooks: tool.execute.after(webfetch) → log real fetches
 *        session.idle                 → diff cited URLs vs fetched URLs → flag hallucinations
 *
 * Place in .opencode/plugins/ (project) or ~/.config/opencode/plugins/ (global).
 */
import type { Plugin } from "@opencode-ai/plugin"
import { join } from "path"

const FETCH_LOG = "/tmp/oc-fetches.jsonl"
const ERROR_LOG_REL = "logs/citation-errors.log"

// Matches [T1]/[T2]/[T3] followed by an https:// URL in assistant messages
const CITATION_RX = /\[T[123]\]\s+(https?:\/\/\S+)/g

export const CitationValidator: Plugin = async ({ directory, $ }) => {
  const errorLog = join(directory, ERROR_LOG_REL)
  await $`mkdir -p ${join(directory, "logs")}`

  return {
    // ── 1. Log every real webfetch call ──────────────────────────────────────
    "tool.execute.after": async (input: any) => {
      if (input.tool !== "webfetch") return
      const url: string = input.args?.url ?? input.args?.input ?? ""
      if (!url) return
      const hasError = !!(input.output?.error)
      const entry = JSON.stringify({ url, success: !hasError, ts: new Date().toISOString() })
      await $`echo ${entry} >> ${FETCH_LOG}`
    },

    // ── 2. On session idle (turn complete): validate citations ────────────────
    "session.idle": async (event: any) => {
      // Extract the last assistant message text from the event
      const messages: any[] = event?.messages ?? event?.session?.messages ?? []
      const lastAssistant = [...messages].reverse().find((m: any) => m.role === "assistant")
      const text: string = lastAssistant?.content ?? ""

      if (!text) return

      // Collect all cited URLs
      const cited: string[] = []
      for (const match of text.matchAll(CITATION_RX)) {
        cited.push(match[1].replace(/[.,;)]+$/, "")) // strip trailing punctuation
      }
      if (cited.length === 0) return

      // Load actually-fetched URLs
      let fetched: Set<string> = new Set()
      try {
        const raw = await Bun.file(FETCH_LOG).text()
        for (const line of raw.split("\n").filter(Boolean)) {
          try {
            const { url, success } = JSON.parse(line)
            if (success) fetched.add(url)
          } catch {}
        }
      } catch {}

      // Diff
      const ts = new Date().toISOString()
      let failures = 0
      for (const url of cited) {
        if (!fetched.has(url)) {
          await $`echo ${`${ts}\tCITATION_HALLUCINATED\t${url}`} >> ${errorLog}`
          failures++
        }
      }

      // Clean up session fetch log
      await $`rm -f ${FETCH_LOG}`.nothrow()

      if (failures > 0) {
        console.warn(`⚠️  [citation-validator] ${failures} cited URL(s) never fetched — see ${ERROR_LOG_REL}`)
      }
    },
  }
}
