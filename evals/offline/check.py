#!/usr/bin/env python3
"""Zero-token check of the dev-brain plugin against the real agent binaries.

The plugin is installed from this repository's marketplace into a throwaway home,
and the model is replaced by evals/offline/mock_model.py, which replays scripted
tool calls and records every request. Nothing reaches a real provider.

Claude Code (required): global rules and saved state reach the session, an oversized
state becomes a notice, workflows expand and stay out of the skill listing, the
reviewer reads the diff with git but cannot write, and commit and push need the user
even when the user's settings allow git.
Codex CLI and Copilot CLI (when found on PATH; an explicit CODEX / COPILOT variable
makes them required): the same plugin installs unchanged; rules and state arrive,
workflows stay out of the skill listing, and git commit is stopped. Copilot's reviewer
must also have no shell. VS Code is not covered: it cannot run here.

It does not judge model behavior; use evals/scenarios/ for that.

usage: python3 evals/offline/check.py
       (CLAUDE / CODEX / COPILOT=<binary> if not on PATH)
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
        self.mock.script(steps)
        subprocess.run([self.claude, "-p", prompt, "--model", "mock-model", *extra], cwd=self.repo,
                       env={**self.env, "PWD": str(self.repo)}, stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=240)
        bodies = self.mock.agent_calls()
        if not bodies:
            check("claude sent a request to the mock model", False)
        return bodies


def function_outputs(bodies):
    """Tool outputs fed back to a Responses-API agent (Codex), once per call id."""
    results = {}
    for body in bodies:
        for item in body.get("input", []):
            if isinstance(item, dict) and item.get("type") == "function_call_output":
                results.setdefault(item.get("call_id"), json.dumps(item.get("output")))
    return list(results.values())


def host_setup(prefix, **extra):
    """A clean environment in a throwaway home, for an agent CLI other than Claude Code."""
    root = Path(tempfile.mkdtemp(prefix=prefix))
    home = root / "home"
    home.mkdir()
    identity = {"GIT_AUTHOR_NAME": "check", "GIT_COMMITTER_NAME": "check",
                "GIT_AUTHOR_EMAIL": "check@example.invalid", "GIT_COMMITTER_EMAIL": "check@example.invalid"}
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home), "LANG": "C.UTF-8", "TERM": "dumb",
           "NO_PROXY": "127.0.0.1,localhost", **identity, **extra}
    return root, env


def host_install(binary, env, *commands):
    for args in commands:
        result = subprocess.run([binary, *args], env=env, capture_output=True, text=True)
        if result.returncode:
            raise SystemExit(f"FAIL  {Path(binary).name} {' '.join(args)}: {result.stdout}{result.stderr}")


def host_run(cmd, env, repo, mock, steps):
    mock.script(steps)
    subprocess.run(cmd, cwd=repo, env={**env, "PWD": str(repo)}, stdin=subprocess.DEVNULL,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=240)
    bodies = mock.agent_calls()
    if not bodies:
        check(f"{Path(cmd[0]).name} sent a request to the mock model", False)
    return bodies


GIT_COMMANDS = ["git status --short", "git commit -am wip", "git push origin main"]


def check_codex(codex, mock):
    root, env = host_setup("dev-brain-offline-codex-", MOCK_KEY="offline-check")
    try:
        host_install(codex, env, ["plugin", "marketplace", "add", str(KIT)], ["plugin", "add", "dev-brain@dev-brain"])
        repo = make_repo(root)
        provider = (f'model_providers.mock={{ name = "mock", base_url = "{mock.url}/v1", '
                    'wire_api = "responses", env_key = "MOCK_KEY" }')

        def run(prompt, steps, *extra):
            cmd = [codex, "exec", "--skip-git-repo-check", "-c", 'model_provider="mock"', "-c", 'model="mock"',
                   "-c", provider, *extra, prompt]
            return host_run(cmd, env, repo, mock, steps)

        # Plugin hooks run only after the user trusts them; the check bypasses that inside its own sandbox.
        trust = "--dangerously-bypass-hook-trust"
        check("codex: hooks wait for the user's trust", RULES not in json.dumps(run("hello", [{"text": "done"}])))
        text = json.dumps(run("hello", [{"text": "done"}], trust))
        check("codex: global rules and saved state arrive once trusted", RULES in text and STATE_MARK in text)
        check("codex: workflows stay out of the skill listing",
              "dev-brain:debugging" in text and "dev-brain:handoff" not in text)
        for name, marker in WORKFLOWS.items():
            bodies = run(f"$dev-brain:{name}", [{"text": "done"}], trust)
            check(f"codex: $dev-brain:{name} expands the workflow", marker in json.dumps(bodies))
        # Without the sandbox the commit would succeed, so only the guard can stop it.
        steps = [{"tool": "exec_command", "args": {"cmd": cmd}} for cmd in GIT_COMMANDS] + [{"text": "done"}]
        before = commit_count(repo)
        results = function_outputs(run("save my work", steps, trust, "-s", "danger-full-access"))
        check("codex: read-only git runs", any("app.txt" in r for r in results))
        guarded = sum("needs your explicit decision" in r for r in results)
        check("codex: commit and push are refused", guarded == 2 and commit_count(repo) == before, f"{guarded}/2 refused")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def check_copilot(copilot, mock):
    root, env = host_setup("dev-brain-offline-copilot-", NO_COLOR="1", COPILOT_OFFLINE="true",
                           COPILOT_PROVIDER_BASE_URL=mock.url, COPILOT_PROVIDER_TYPE="anthropic",
                           COPILOT_PROVIDER_API_KEY="sk-offline-check", COPILOT_MODEL="mock-model",
                           COPILOT_PROVIDER_MODEL_ID="claude-sonnet-4.5", COPILOT_PROVIDER_WIRE_MODEL="mock-model")
    env["COPILOT_HOME"] = str(Path(env["HOME"]) / ".copilot")
    Path(env["COPILOT_HOME"]).mkdir()
    try:
        host_install(copilot, env, ["plugin", "marketplace", "add", str(KIT)], ["plugin", "install", "dev-brain@dev-brain"])
        repo = make_repo(root)

        def run(prompt, steps, *extra):
            return host_run([copilot, "-p", prompt, *extra], env, repo, mock, steps)

        text = json.dumps(run("hello", [{"text": "done"}]))
        check("copilot: global rules and saved state arrive", RULES in text and STATE_MARK in text)
        check("copilot: workflows stay out of the skill listing",
              "<name>debugging</name>" in text and "<name>handoff</name>" not in text)
        steps = [{"tool": "bash", "args": {"command": cmd, "description": "git", "mode": "sync", "initial_wait": 30}}
                 for cmd in GIT_COMMANDS] + [{"text": "done"}]
        before = commit_count(repo)
        results = tool_results(run("save my work", steps, "--allow-all-tools"))
        check("copilot: read-only git runs", any("app.txt" in r for r in results))
        guarded = sum("needs your explicit decision" in r for r in results)
        check("copilot: commit and push are stopped", guarded == 2 and commit_count(repo) == before, f"{guarded}/2 stopped")
        steps = [{"tool": "task", "args": {"description": "review changes", "prompt": "Review all changes.",
                                           "agent_type": "dev-brain:reviewer", "name": "rev", "mode": "sync"}},
                 {"text": "no findings"}, {"text": "done"}]
        bodies = run("check the changes", steps)
        tools = {tool["name"] for body in bodies if "independent reviewer" in json.dumps(body.get("system"))
                 for tool in body["tools"]}
        check("copilot: the reviewer has read tools only", bool(tools) and tools <= {"view", "grep", "glob"}, str(sorted(tools)))
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

        for name, variable, check_host in (("codex", "CODEX", check_codex), ("copilot", "COPILOT", check_copilot)):
            binary = shutil.which(os.environ.get(variable) or name)
            if binary:
                check_host(binary, mock)
            elif os.environ.get(variable):
                check(f"{name} found", False, f"{variable}={os.environ[variable]}")
            else:
                print(f"SKIP  {name}: not on PATH (set {variable}=<binary> to require it)")
    finally:
        mock.server.shutdown()
        shutil.rmtree(sandbox.root, ignore_errors=True)
    print("ALL PASS" if not failures else f"{len(failures)} FAILED")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
