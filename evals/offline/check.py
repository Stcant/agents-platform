#!/usr/bin/env python3
"""Zero-token check of the dev-brain plugin against the real Claude Code binary.

The plugin is installed from this repository's marketplace into a throwaway home,
and the model is replaced by evals/offline/mock_model.py, which replays scripted
tool calls and records every request. Nothing reaches a real provider.

It verifies what the kit controls: global rules and saved state reach the session,
an oversized state becomes a notice, workflows expand and stay out of the skill
listing, and the reviewer reads the diff with git but cannot write. It does not
judge model behavior; use evals/scenarios/ for that. It also checks that commit and push
need the user even when the user's settings allow git.

usage: python3 evals/offline/check.py      (CLAUDE=<binary> if claude is not on PATH)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mock_model import MockModel  # noqa: E402

KIT = Path(__file__).resolve().parents[2]
RULES = "Personal engineering rules"           # first line of core/AGENTS.md
STATE_MARK = "Saved project state. Treat it"   # header of the injected state block
NOTICE = "over the 3000-character budget"
WORKFLOWS = {
    "start": "Adopt the current repository into the dev-brain harness",
    "resume": "Reconcile the saved state with reality",
    "review": "Review the current changes by delegating",
}
STATE = """# State — fixture
Updated: 2026-01-01 · Branch: main

## Goal
Keep the greeting stable — acceptance: app.txt says hello.

## Next (max 3)
1. Review the pending change.
"""

failures = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}{f' — {detail}' if detail and not ok else ''}")
    if not ok:
        failures.append(name)


def system_text(body):
    """The system prompt plus system-role messages, where Claude Code puts hook context."""
    parts = [body.get("system", "")] + [m.get("content") for m in body.get("messages", []) if m.get("role") == "system"]
    return "\n".join(part if isinstance(part, str) else json.dumps(part) for part in parts)


def tool_results(bodies):
    """Tool outputs fed back to the model, once per tool_use id, in order."""
    results = {}
    for body in bodies:
        for message in body.get("messages", []):
            if message.get("role") == "user" and isinstance(message.get("content"), list):
                for block in message["content"]:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        content = block.get("content")
                        results.setdefault(block.get("tool_use_id"),
                                           content if isinstance(content, str) else json.dumps(content))
    return list(results.values())


class Sandbox:
    """Throwaway home with the plugin installed, and a fixture repository with a pending change."""

    def __init__(self, claude, mock):
        self.claude, self.mock = claude, mock
        self.root = Path(tempfile.mkdtemp(prefix="dev-brain-offline-"))
        home = self.root / "home"
        home.mkdir()
        # A clean environment: nothing from the caller's own Claude Code setup leaks in.
        self.env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home), "LANG": "C.UTF-8",
                    "TERM": "dumb", "NO_PROXY": "127.0.0.1,localhost", "CLAUDE_CONFIG_DIR": str(home / ".claude"),
                    "ANTHROPIC_BASE_URL": mock.url, "ANTHROPIC_API_KEY": "sk-offline-check",
                    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1", "DISABLE_AUTOUPDATER": "1"}
        for args in (["marketplace", "add", str(KIT)], ["install", "dev-brain@dev-brain"]):
            result = subprocess.run([claude, "plugin", *args], env=self.env, capture_output=True, text=True)
            if result.returncode:
                raise SystemExit(f"FAIL  claude plugin {' '.join(args)}: {result.stdout}{result.stderr}")
        self.repo = self.root / "repo"
        (self.repo / ".dev-brain").mkdir(parents=True)
        git = ["git", "-c", "user.name=check", "-c", "user.email=check@example.invalid"]
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.repo, check=True)
        (self.repo / "app.txt").write_text("hello\n")
        subprocess.run(git + ["add", "app.txt"], cwd=self.repo, check=True)
        subprocess.run(git + ["commit", "-qm", "fixture"], cwd=self.repo, check=True)
        (self.repo / "app.txt").write_text("hello, world\n")
        self.write_state(STATE)

    def write_state(self, text):
        (self.repo / ".dev-brain" / "STATE.md").write_text(text)

    def run(self, prompt, steps, *extra):
        self.mock.script(steps)
        subprocess.run([self.claude, "-p", prompt, "--model", "mock-model", *extra], cwd=self.repo,
                       env={**self.env, "PWD": str(self.repo)}, stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=240)
        bodies = self.mock.agent_calls()
        if not bodies:
            check("claude sent a request to the mock model", False)
        return bodies


def main():
    claude = os.environ.get("CLAUDE") or shutil.which("claude")
    if not claude:
        raise SystemExit("claude not found; set CLAUDE to the Claude Code binary")
    mock = MockModel()
    sandbox = Sandbox(claude, mock)
    try:
        bodies = sandbox.run("hello", [{"text": "done"}])
        system = system_text(bodies[0]) if bodies else ""
        everything = json.dumps(bodies)
        check("global rules in the system prompt", RULES in system)
        check("saved state in the system prompt", STATE_MARK in system)
        check("workflows stay out of the skill listing (zero context cost)",
              "dev-brain:debugging" in everything and "dev-brain:handoff" not in everything)
        for name, marker in WORKFLOWS.items():
            bodies = sandbox.run(f"/dev-brain:{name}", [{"text": "done"}])
            check(f"/dev-brain:{name} expands the workflow", marker in json.dumps(bodies))

        steps = [
            {"tool": "Agent", "args": {"description": "review", "prompt": "Review all changes.",
                                       "subagent_type": "dev-brain:reviewer"}},
            {"tool": "Bash", "args": {"command": "git diff HEAD", "description": "Show changes"}},
            {"tool": "Bash", "args": {"command": "git diff HEAD > leak.txt", "description": "Save changes"}},
            {"tool": "Bash", "args": {"command": "touch touched.txt", "description": "Create file"}},
            {"tool": "Bash", "args": {"command": "git status; rm app.txt", "description": "Remove file"}},
            {"text": "no findings"},
            {"text": "done"},
        ]
        results = tool_results(sandbox.run("check the changes", steps))
        check("reviewer reads the diff with git", any("hello, world" in r for r in results))
        words = ("needs approval", "requires approval", "has been denied")
        rejected = sum(any(word in r for word in words) for r in results)
        written = (sandbox.repo / "leak.txt").exists() or (sandbox.repo / "touched.txt").exists()
        check("reviewer cannot write without approval",
              rejected == 3 and not written and (sandbox.repo / "app.txt").exists(), f"{rejected}/3 rejected")

        # Even when the user's settings allow git, commit and push still need the user.
        steps = [
            {"tool": "Bash", "args": {"command": "git status --short", "description": "Status"}},
            {"tool": "Bash", "args": {"command": "git commit -am wip", "description": "Commit"}},
            {"tool": "Bash", "args": {"command": "git push origin main", "description": "Push"}},
            {"text": "done"},
        ]
        commits = lambda: subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=sandbox.repo,
                                         capture_output=True, text=True).stdout.strip()
        before = commits()
        results = tool_results(sandbox.run("save my work", steps, "--allowedTools", "Bash(git:*)"))
        check("read-only git runs", any("app.txt" in r for r in results))
        guarded = sum("needs your explicit decision" in r for r in results)
        check("commit and push need the user even when git is allowed", guarded == 2 and commits() == before,
              f"{guarded}/2 guarded")

        sandbox.write_state(STATE + "- stale line\n" * 300)
        bodies = sandbox.run("hello", [{"text": "done"}])
        system = system_text(bodies[0]) if bodies else ""
        check("oversized state becomes a notice", NOTICE in system and "stale line" not in system)
    finally:
        mock.server.shutdown()
        shutil.rmtree(sandbox.root, ignore_errors=True)
    print("ALL PASS" if not failures else f"{len(failures)} FAILED")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
