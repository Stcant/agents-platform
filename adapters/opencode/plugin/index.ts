import { Plugin } from "@opencode/plugin"
import { execFileSync } from "node:child_process"
import { statSync } from "node:fs"
import { join } from "node:path"
import { fileURLToPath } from "node:url"

// The state text and its size budget come from the shared core script, so every
// agent adapter injects exactly the same thing.
const CONTEXT_SCRIPT = fileURLToPath(new URL("../../../core/bin/dev-brain-context", import.meta.url))
const STATE_PATH = ".dev-brain/STATE.md"

function stateVersion(root: string): string {
  try {
    const stat = statSync(join(root, STATE_PATH))
    return `${stat.mtimeMs}:${stat.size}`
  } catch {
    return "none"
  }
}

export default Plugin.define({
  id: "dev-brain",
  async setup(ctx) {
    const root = ctx.location.project?.canonical ?? ctx.location.directory
    let cached: { version: string; text: string } | undefined

    // The context hook runs on every model call: rerun the script only when the file changes.
    function contextText(): string {
      const version = stateVersion(root)
      if (cached?.version !== version) {
        let text = ""
        try {
          text = execFileSync("python3", [CONTEXT_SCRIPT, "--format", "text", "--root", root], {
            encoding: "utf8",
            timeout: 5000,
          }).trim()
        } catch {
          // Without python3 nothing is injected; the global rules tell the agent to read the file.
        }
        cached = { version, text }
      }
      return cached.text
    }

    // Subagent sessions (reviewer, explore, ...) get a focused prompt from their parent;
    // the project state would only add tokens to each of their calls.
    const isSubagent = new Map<string, boolean>()

    async function isSubagentSession(sessionID: string): Promise<boolean> {
      const known = isSubagent.get(sessionID)
      if (known !== undefined) return known
      try {
        const session = await ctx.session.get({ sessionID })
        const child = session.parentID !== undefined
        isSubagent.set(sessionID, child)
        return child
      } catch {
        return false
      }
    }

    await ctx.session.hook("context", async (event) => {
      if (await isSubagentSession(event.sessionID)) return
      const text = contextText()
      if (text) event.system.push({ type: "text", text })
    })

    await ctx.session.hook("compaction", (event) => {
      event.system.push({
        type: "text",
        text: "Preserve in the summary, in this order: current goal and acceptance criteria, verified evidence (command + PASS/FAIL/NOT RUN), blockers and failed attempts, and the next executable action. These are written to .dev-brain/STATE.md after the session.",
      })
    })
  },
})
