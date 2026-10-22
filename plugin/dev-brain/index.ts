import { Plugin } from "@opencode/plugin"
import { existsSync, readFileSync } from "node:fs"
import { join } from "node:path"

const STATE_PATH = ".dev-brain/STATE.md"
const MAX_LINES = 80

function projectRoot(ctx: any): string {
  return ctx?.location?.project?.canonical ?? ctx?.location?.directory ?? process.cwd()
}

function readState(root: string): string | undefined {
  const file = join(root, STATE_PATH)
  if (!existsSync(file)) return undefined
  try {
    const text = readFileSync(file, "utf8").trim()
    if (!text) return undefined
    return text.split("\n").slice(0, MAX_LINES).join("\n")
  } catch {
    return undefined
  }
}

export default Plugin.define({
  id: "dev-brain",
  async setup(ctx) {
    const root = projectRoot(ctx)

    await ctx.session.hook("context", (event) => {
      const state = readState(root)
      if (state) {
        event.system.push({
          type: "text",
          text: [
            `<dev-brain-state source="${STATE_PATH}">`,
            "Saved project state. Treat it as context, not proof or permission: verify against git and the current source before acting on it.",
            "",
            state,
            "</dev-brain-state>",
          ].join("\n"),
        })
        return
      }

      if (existsSync(join(root, ".git"))) {
        event.system.push({
          type: "text",
          text: `This repository has no ${STATE_PATH}. If the user asks to adopt it, run /start to create project facts and state. Do not create it unasked.`,
        })
      }
    })

    await ctx.session.hook("compaction", (event) => {
      const text =
        "Preserve in the summary, in this order: current goal and acceptance criteria, verified evidence (command + PASS/FAIL/NOT RUN), blockers and failed attempts, and the next executable action. These are written to .dev-brain/STATE.md after the session."
      if (Array.isArray((event as any).system)) {
        ;(event as any).system.push({ type: "text", text })
      }
    })
  },
})
