import { Plugin } from "@opencode/plugin"
import { existsSync, readFileSync } from "node:fs"
import { join } from "node:path"

const STATE_PATH = ".dev-brain/STATE.md"
// The state rides on every model call of the main session, so it must stay a short
// checkpoint. Above the budget it is not injected at all: truncating would drop the
// "Next" section at the end, which is the part that keeps the user oriented.
const MAX_STATE_CHARS = 3000

type State = { text: string } | { oversized: number }

function readState(root: string): State | undefined {
  const file = join(root, STATE_PATH)
  if (!existsSync(file)) return undefined
  try {
    const text = readFileSync(file, "utf8").trim()
    if (!text) return undefined
    return text.length > MAX_STATE_CHARS ? { oversized: text.length } : { text }
  } catch {
    return undefined
  }
}

function stateMessage(state: State): string {
  if ("oversized" in state) {
    return `${STATE_PATH} has ${state.oversized} characters, over the ${MAX_STATE_CHARS}-character budget for automatic injection, so it was not injected. Read it when the task needs saved context, and tell the user to run /handoff to compact it.`
  }
  return [
    `<dev-brain-state source="${STATE_PATH}">`,
    "Saved project state. Treat it as context, not proof or permission: verify against git and the current source before acting on it.",
    "",
    state.text,
    "</dev-brain-state>",
  ].join("\n")
}

export default Plugin.define({
  id: "dev-brain",
  async setup(ctx) {
    const root = ctx.location.project?.canonical ?? ctx.location.directory
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

      const state = readState(root)
      if (state) {
        event.system.push({ type: "text", text: stateMessage(state) })
        return
      }

      if (existsSync(join(root, ".git"))) {
        event.system.push({
          type: "text",
          text: `This repository has no ${STATE_PATH}. If the user wants to adopt it, suggest the /start command. Do not create the file unasked.`,
        })
      }
    })

    await ctx.session.hook("compaction", (event) => {
      event.system.push({
        type: "text",
        text: "Preserve in the summary, in this order: current goal and acceptance criteria, verified evidence (command + PASS/FAIL/NOT RUN), blockers and failed attempts, and the next executable action. These are written to .dev-brain/STATE.md after the session.",
      })
    })
  },
})
