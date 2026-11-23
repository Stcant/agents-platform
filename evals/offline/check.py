#!/usr/bin/env python3
"""Zero-token check of the dev-brain plugin against the real agent binaries.

The plugin is installed from this repository's marketplace into a throwaway home,
and the model is replaced by evals/offline/mock_model.py, which replays scripted
tool calls and records every request. Nothing reaches a real provider.

Claude Code (required): global rules and saved state reach the session, an oversized
state becomes a notice, workflows expand and stay out of the skill listing, the
reviewer reads the diff with git but cannot write, and commit and push need the user
even when the user's settings allow git.
OpenCode (when found on PATH; an explicit OPENCODE variable makes it required): the
adapter in adapters/opencode loads; rules and state reach the main session and not the
subagent, workflows stay out of the skill listing, commit and push need the user, and
the reviewer reads the diff but cannot write.

It does not judge model behavior; use evals/scenarios/ for that.

usage: python3 evals/offline/check.py
       (CLAUDE / OPENCODE=<binary> if not on PATH)
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


def make_repo(root):
    """Fixture repository with one commit, a pending change and a small saved state."""
    repo = root / "repo"
    (repo / ".dev-brain").mkdir(parents=True)
    git = ["git", "-c", "user.name=check", "-c", "user.email=check@example.invalid"]
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    (repo / "app.txt").write_text("hello\n")
    subprocess.run(git + ["add", "app.txt"], cwd=repo, check=True)
    subprocess.run(git + ["commit", "-qm", "fixture"], cwd=repo, check=True)
    (repo / "app.txt").write_text("hello, world\n")
    (repo / ".dev-brain" / "STATE.md").write_text(STATE)
    return repo


def commit_count(repo):
    return subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()


def run_agent(cmd, env, repo, mock, steps):
    """Run an agent CLI once against the mock model; returns the agent-loop requests it sent."""
    mock.script(steps)
    subprocess.run(cmd, cwd=repo, env={**env, "PWD": str(repo)}, stdin=subprocess.DEVNULL,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=240)
    bodies = mock.agent_calls()
    if not bodies:
        check(f"{Path(cmd[0]).name} sent a request to the mock model", False)
    return bodies


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
        self.repo = make_repo(self.root)

    def write_state(self, text):
        (self.repo / ".dev-brain" / "STATE.md").write_text(text)

    def run(self, prompt, steps, *extra):
        cmd = [self.claude, "-p", prompt, "--model", "mock-model", *extra]
        return run_agent(cmd, self.env, self.repo, self.mock, steps)


GIT_COMMANDS = ["git status --short", "git commit -am wip", "git push origin main"]


def chat_results(bodies):
    """Tool outputs fed back to a chat-completions agent (OpenCode), once per call id."""
    results = {}
    for body in bodies:
        for message in body.get("messages", []):
            if message.get("role") == "tool":
                content = message.get("content")
                results.setdefault(message.get("tool_call_id"), content if isinstance(content, str) else json.dumps(content))
    return list(results.values())


def check_opencode(opencode, mock):
    root = Path(tempfile.mkdtemp(prefix="dev-brain-offline-opencode-"))
    home = root / "home"
    config = home / ".config" / "opencode"
    config.mkdir(parents=True)
    # Only the adapter is configured: it brings the skills, the guard and the reviewer with it.
    (config / "opencode.json").write_text(json.dumps({
        "model": "mock/mock", "plugins": [str(KIT / "adapters" / "opencode")],
        "providers": {"mock": {
            "name": "Mock", "package": "@opencode/ai/providers/openai-compatible",
            "settings": {"baseURL": mock.url + "/v1"},
            "models": {"mock": {"name": "Mock", "capabilities": {"tools": True, "input": ["text"], "output": ["text"]},
                                "limit": {"context": 200000, "output": 8000}}}}}}))
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home), "LANG": "C.UTF-8", "TERM": "dumb",
           "NO_PROXY": "127.0.0.1,localhost", "XDG_CONFIG_HOME": str(home / ".config"),
           "XDG_DATA_HOME": str(home / ".local/share"), "XDG_STATE_HOME": str(home / ".local/state"),
           "XDG_CACHE_HOME": str(home / ".cache"), "OPENCODE_DISABLE_MODELS_FETCH": "1",
           "OPENCODE_DISABLE_FREE_MODELS": "1", "GIT_AUTHOR_NAME": "check", "GIT_COMMITTER_NAME": "check",
           "GIT_AUTHOR_EMAIL": "check@example.invalid", "GIT_COMMITTER_EMAIL": "check@example.invalid"}
    try:
        repo = make_repo(root)

        def run(prompt, steps):
            return run_agent([opencode, "run", "--standalone", "-m", "mock/mock", prompt], env, repo, mock, steps)

        def is_main(body):
            return any(tool["function"]["name"] == "edit" for tool in body["tools"])

        # The reviewer runs in the background, so each step says which session it belongs to.
        mine, theirs = {"unless": "independent reviewer"}, {"when": "independent reviewer"}
        steps = [{"tool": "subagent", "args": {"agent": "reviewer", "description": "review", "prompt": "Review all changes."}, **mine},
                 {"tool": "shell", "args": {"command": "git diff HEAD"}, **theirs},
                 {"tool": "shell", "args": {"command": "git diff HEAD > leak.txt"}, **theirs},
                 {"tool": "shell", "args": {"command": "git diff HEAD --output=leak.txt"}, **theirs},
                 {"tool": "shell", "args": {"command": "git status; rm app.txt"}, **theirs},
                 {"tool": "shell", "args": {"command": "git diff HEAD $(touch touched.txt)"}, **theirs},
                 {"tool": "shell", "args": {"command": "git diff HEAD `touch touched.txt`"}, **theirs},
                 {"text": "no findings", **theirs}, {"text": "done", **mine}]
        bodies = run("check", steps)
        main = [b for b in bodies if is_main(b)]
        child = [b for b in bodies if not is_main(b)]
        results = chat_results(bodies)
        check("opencode: global rules and saved state reach the main session",
              bool(main) and all(RULES in system_text(b) and STATE_MARK in system_text(b) for b in main))
        check("opencode: rules and state stay out of the subagent",
              bool(child) and not any(RULES in system_text(b) or STATE_MARK in system_text(b) for b in child))
        text = json.dumps(main[0]) if main else ""
        check("opencode: workflows stay out of the skill listing",
              "<id>debugging</id>" in text and "<id>handoff</id>" not in text)
        check("opencode: reviewer reads the diff with git", any("hello, world" in r for r in results))
        rejected = sum(any(word in r for word in ("rejected", "denied", "not allowed")) for r in results)
        check("opencode: reviewer cannot write (>, --output, rm, substitution)",
              rejected == 5 and not any((repo / name).exists() for name in ("leak.txt", "touched.txt"))
              and (repo / "app.txt").exists(), f"{rejected}/5 rejected")

        bodies = run("start the harness", [{"tool": "skill", "args": {"id": "start"}}, {"text": "done"}])
        check("opencode: a workflow loads by id", any(WORKFLOWS["start"] in r for r in chat_results(bodies)))

        # The fixture has a git identity, so only the guard can keep the commit from happening.
        steps = [{"tool": "shell", "args": {"command": cmd}} for cmd in GIT_COMMANDS] + [{"text": "done"}]
        before = commit_count(repo)
        results = chat_results(run("save my work", steps))
        check("opencode: read-only git runs", any("app.txt" in r for r in results))
        guarded = sum("cannot ask the user" in r for r in results)
        check("opencode: commit and push need the user", guarded == 2 and commit_count(repo) == before, f"{guarded}/2 guarded")

        (repo / ".dev-brain" / "STATE.md").write_text(STATE + "- stale line\n" * 300)
        bodies = run("hello", [{"text": "done"}])
        system = system_text(bodies[0]) if bodies else ""
        check("opencode: oversized state becomes a notice", NOTICE in system and "stale line" not in system)
    finally:
        shutil.rmtree(root, ignore_errors=True)


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
        commits = lambda: commit_count(sandbox.repo)
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

        binary = shutil.which(os.environ.get("OPENCODE") or "opencode")
        if binary:
            check_opencode(binary, mock)
        elif os.environ.get("OPENCODE"):
            check("opencode found", False, f"OPENCODE={os.environ['OPENCODE']}")
        else:
            print("SKIP  opencode: not on PATH (set OPENCODE=<binary> to require it)")
    finally:
        mock.server.shutdown()
        shutil.rmtree(sandbox.root, ignore_errors=True)
    print("ALL PASS" if not failures else f"{len(failures)} FAILED")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
