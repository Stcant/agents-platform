// OpenCode adapter for dev-brain: a thin layer over core/, with no rule of its own.
//   - rules + saved state: runs core/bin/dev-brain-context for the main session
//   - git guard: runs core/bin/dev-brain-guard on every shell command
//   - skills: registers core/skills (workflows are not offered to the model)
//   - reviewer: built from core/agents/reviewer.md (prompt and read-only tool list)
// Install: add this directory to `plugins` in opencode.json (see README).
import type { Plugin } from "@opencode/plugin"
import { execFileSync } from "node:child_process"
import { readFileSync, readdirSync } from "node:fs"
import { join } from "node:path"
import { fileURLToPath } from "node:url"

const CORE = fileURLToPath(new URL("../../core/", import.meta.url))

// Frontmatter as flat `key: value` lines, which is all the kit's files use.
function readMarkdown(file: string): { meta: Record<string, string>; body: string } {
  const match = readFileSync(file, "utf8").match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/)
  const meta: Record<string, string> = {}
  for (const line of (match?.[1] ?? "").split("\n")) {
    const at = line.indexOf(":")
    if (at > 0) meta[line.slice(0, at).trim()] = line.slice(at + 1).trim()
  }
  return { meta, body: (match?.[2] ?? "").trim() }
}

function runScript(name: string, args: string[], input: string | undefined, cwd: string): string {
  return execFileSync("python3", [join(CORE, "bin", name), ...args], { cwd, input, encoding: "utf8", timeout: 5000 }).trim()
}

// Claude's `tools: Read, Grep, Glob, Bash(git diff:*)` as OpenCode permissions: everything is denied
// except what the list names, and the base policy's "ask" rules (such as .env files) stay.
type Rule = { action: string; resource: string; effect: "allow" | "deny" | "ask" }

function permissionsFor(tools: string, base: Rule[]): Rule[] {
  const allow = (action: string, resource = "*"): Rule => ({ action, resource, effect: "allow" })
  const names: Record<string, string> = { Read: "read", Grep: "grep", Glob: "glob" }
  const rules = tools.split(/,\s*(?![^()]*\))/).flatMap((tool) => {
    const bash = tool.trim().match(/^Bash\((.+?):\*\)$/)
    if (bash) return [allow("shell", `${bash[1]} *`)]
    return names[tool.trim()] ? [allow(names[tool.trim()])] : []
  })
  // The shell matcher checks each chained command but not redirections, so those are denied by name.
  const writes = ["* --output*", "*>*"].map((resource): Rule => ({ action: "shell", resource, effect: "deny" }))
  return [{ action: "*", resource: "*", effect: "deny" }, ...rules, ...base.filter((rule) => rule.effect === "ask"), ...writes]
}

const plugin: Plugin.Plugin = {
  id: "dev-brain",
  async setup(ctx) {
    const project = ctx.location.directory

    // Subagents get a focused prompt from their parent; the rules and state are for the main session
    // (Claude Code's SessionStart hook does not run for them either).
    const subagent = new Map<string, boolean>()
    async function isSubagent(sessionID: string) {
      if (!subagent.has(sessionID)) {
        const session = await ctx.session.get({ sessionID }).catch(() => undefined)
        subagent.set(sessionID, session?.parentID !== undefined)
      }
      return subagent.get(sessionID)
    }

    await ctx.session.hook("context", async (event) => {
      if (await isSubagent(event.sessionID)) return
      let text = ""
      try {
        text = runScript("dev-brain-context", ["--text"], undefined, project)
      } catch {
        text = "dev-brain could not load its rules and saved state (is python3 installed?). Tell the user."
      }
      event.system.push({ type: "text", text })
    })

    // The permission policy cannot see inside a git command, so the shared guard decides; "ask" is the
    // same answer it gives Claude Code. An explicit deny in the user's config is final and never gets here.
    await ctx.permission.hook("evaluate", (event) => {
      if (event.action !== "shell" || event.effect === "deny") return
      for (const command of event.resources) {
        let reason: string | undefined
        try {
          const answer = runScript("dev-brain-guard", [], JSON.stringify({ tool_input: { command } }), project)
          reason = answer ? JSON.parse(answer).hookSpecificOutput.permissionDecisionReason : undefined
        } catch {
          reason = "dev-brain could not check this command (is python3 installed?)"
        }
        if (reason) {
          event.effect = "ask"
          event.message = reason
          return
        }
      }
    })

    await ctx.skill.transform((editor) => {
      for (const dir of readdirSync(join(CORE, "skills"))) {
        const path = join(CORE, "skills", dir, "SKILL.md")
        const { meta, body } = readMarkdown(path)
        editor.add({
          id: meta.name,
          name: meta.name,
          description: meta.description,
          autoinvoke: meta["disable-model-invocation"] !== "true",
          path,
          content: body,
        } as never)
      }
    })

    await ctx.agent.transform((editor) => {
      const { meta, body } = readMarkdown(join(CORE, "agents", "reviewer.md"))
      editor.update(meta.name, (agent) => {
        agent.mode = "subagent"
        agent.description = meta.description
        agent.system = body
        agent.permissions = permissionsFor(meta.tools, agent.permissions)
      })
    })
  },
}

export default plugin
