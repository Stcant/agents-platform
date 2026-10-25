#!/usr/bin/env python3
"""Zero-token check of the installed kit against the real agent binaries.

For every agent CLI found (opencode, claude, codex; override with OPENCODE,
CLAUDE, CODEX), the kit is installed into a throwaway home with install.py and
the model is replaced by evals/offline/mock_model.py, which replays scripted
tool calls and records every request. Nothing reaches a real provider.

It verifies what the kit controls: global rules and saved state reach the agent,
an oversized state becomes a notice, workflows expand, and the reviewer reads
the diff with git but cannot write. It does not judge model behavior; use
evals/scenarios/ for that. Cursor has no headless CLI here: its generated files
are only checked for presence.

usage: python3 evals/offline/check.py
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
REVIEW_FLOW = "Review the current changes by delegating"  # core/workflows/review
START_FLOW = "Adopt the current repository into the dev-brain harness"  # core/workflows/start
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


def text_of(value):
    return value if isinstance(value, str) else json.dumps(value)


def system_text(body):
    """System and developer instructions of one request, in any of the three wire formats."""
    parts = [text_of(body.get("system", "")), text_of(body.get("instructions", ""))]
    for message in body.get("messages") or body.get("input") or []:
        if isinstance(message, dict) and message.get("role") in ("system", "developer"):
            parts.append(text_of(message.get("content")))
    return "\n".join(parts)


def tool_results(bodies):
    """Tool outputs fed back to the model, once per call id, in order."""
    results = {}
    for body in bodies:
        for message in body.get("messages") or body.get("input") or []:
            if not isinstance(message, dict):
                continue
            if message.get("role") == "tool":  # chat completions
                results.setdefault(message.get("tool_call_id"), text_of(message.get("content")))
            if message.get("type") == "function_call_output":  # responses
                results.setdefault(message.get("call_id"), text_of(message.get("output")))
            if message.get("role") == "user" and isinstance(message.get("content"), list):  # anthropic
                for block in message["content"]:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        results.setdefault(block.get("tool_use_id"), text_of(block.get("content")))
    return list(results.values())


def binary(name, variable):
    path = os.environ.get(variable) or shutil.which(name)
    return path if path and Path(path).exists() else None


class Sandbox:
    """Throwaway home, fixture repository and installed kit."""

    def __init__(self, tools, bins):
        self.root = Path(tempfile.mkdtemp(prefix="dev-brain-offline-"))
        home = self.root / "home"
        home.mkdir()
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        for name, path in bins.items():
            (bin_dir / name).symlink_to(path)
        # A clean environment: nothing from the caller's own agent setup leaks in.
        self.env = {"PATH": f"{bin_dir}:{os.environ.get('PATH', '/usr/bin:/bin')}", "HOME": str(home),
                    "LANG": "C.UTF-8", "TERM": "dumb", "NO_PROXY": "127.0.0.1,localhost",
                    "XDG_CONFIG_HOME": str(home / ".config"), "XDG_DATA_HOME": str(home / ".local/share"),
                    "XDG_STATE_HOME": str(home / ".local/state"), "XDG_CACHE_HOME": str(home / ".cache"),
                    "CLAUDE_CONFIG_DIR": str(home / ".claude"), "CODEX_HOME": str(home / ".codex")}
        self.repo = self.root / "repo"
        (self.repo / ".dev-brain").mkdir(parents=True)
        git = ["git", "-c", "user.name=check", "-c", "user.email=check@example.invalid"]
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.repo, check=True)
        (self.repo / "app.txt").write_text("hello\n")
        subprocess.run(git + ["add", "app.txt"], cwd=self.repo, check=True)
        subprocess.run(git + ["commit", "-qm", "fixture"], cwd=self.repo, check=True)
        (self.repo / "app.txt").write_text("hello, world\n")
        self.small_state()
        result = subprocess.run([sys.executable, str(KIT / "install.py"), *tools], env=self.env,
                                capture_output=True, text=True)
        if result.returncode:
            raise SystemExit(f"FAIL  install.py: {result.stdout}{result.stderr}")

    def small_state(self):
        (self.repo / ".dev-brain" / "STATE.md").write_text(STATE)

    def big_state(self):
        (self.repo / ".dev-brain" / "STATE.md").write_text(STATE + "- stale line\n" * 300)

    def clean_repo(self):
        for name in ("leak.txt", "touched.txt"):
            (self.repo / name).unlink(missing_ok=True)
        (self.repo / "app.txt").write_text("hello, world\n")

    def run(self, mock, cmd, steps, env=None):
        mock.script(steps)
        subprocess.run(cmd, cwd=self.repo, env={**self.env, "PWD": str(self.repo), **(env or {})},
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=240)
        bodies = mock.agent_calls()
        if not bodies:
            check(f"{Path(cmd[0]).name} sent a request to the mock model", False)
        return bodies


def write_protected(sandbox, results, expected_rejections):
    words = ("permission.rejected", "needs approval", "requires approval", "has been denied")
    rejected = sum(any(word in r for word in words) for r in results)
    return (rejected == expected_rejections and not (sandbox.repo / "leak.txt").exists()
            and not (sandbox.repo / "touched.txt").exists() and (sandbox.repo / "app.txt").exists()), rejected


def check_opencode(sandbox, mock, opencode):
    config_file = Path(sandbox.env["XDG_CONFIG_HOME"]) / "opencode" / "opencode.json"
    config = json.loads(config_file.read_text())
    config["model"] = "mock/mock"
    config["providers"] = {"mock": {
        "name": "Mock", "package": "@opencode/ai/providers/openai-compatible",
        "settings": {"baseURL": mock.url + "/v1"},
        "models": {"mock": {"name": "Mock", "capabilities": {"tools": True, "input": ["text"], "output": ["text"]},
                            "limit": {"context": 200000, "output": 8000}}}}}
    config_file.write_text(json.dumps(config))
    cmd = [opencode, "run", "--standalone", "-m", "mock/mock", "check"]
    env = {"OPENCODE_DISABLE_MODELS_FETCH": "1", "OPENCODE_DISABLE_FREE_MODELS": "1"}
    steps = [
        {"tool": "subagent", "args": {"agent": "reviewer", "description": "review", "prompt": "Review all changes."}},
        {"tool": "shell", "args": {"command": "git diff HEAD"}},
        {"tool": "shell", "args": {"command": "git diff HEAD > leak.txt"}},
        {"tool": "shell", "args": {"command": "git diff HEAD --output=leak.txt"}},
        {"tool": "shell", "args": {"command": "git status; rm app.txt"}},
        {"text": "no findings"},
        {"text": "done"},
    ]
    bodies = sandbox.run(mock, cmd, steps, env)
    main = [b for b in bodies if any(t["function"]["name"] == "edit" for t in b["tools"])]
    child = [b for b in bodies if b not in main]
    results = tool_results(bodies)
    check("opencode: global rules loaded", bool(main) and RULES in system_text(main[0]))
    start = Path(sandbox.env["XDG_CONFIG_HOME"]) / "opencode" / "commands" / "start.md"
    check("opencode: /start command generated", start.exists() and START_FLOW in start.read_text())
    check("opencode: state in the main session", bool(main) and all(STATE_MARK in system_text(b) for b in main))
    check("opencode: state not in the subagent", bool(child) and not any(STATE_MARK in system_text(b) for b in child))
    check("opencode: reviewer reads the diff with git", any("hello, world" in r for r in results))
    ok, rejected = write_protected(sandbox, results, 3)
    check("opencode: reviewer cannot write (>, --output, rm)", ok, f"{rejected}/3 rejected")

    sandbox.big_state()
    bodies = sandbox.run(mock, cmd, [{"text": "done"}], env)
    system = system_text(bodies[0]) if bodies else ""
    check("opencode: oversized state becomes a notice", NOTICE in system and "stale line" not in system)
    sandbox.small_state()
    sandbox.clean_repo()


def check_claude(sandbox, mock, claude):
    env = {"ANTHROPIC_BASE_URL": mock.url, "ANTHROPIC_API_KEY": "sk-offline-check",
           "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1", "DISABLE_AUTOUPDATER": "1"}

    def cmd(prompt):
        return [claude, "-p", prompt, "--model", "mock-model"]

    bodies = sandbox.run(mock, cmd("/dev-brain:review"), [{"text": "done"}], env)
    everything = json.dumps(bodies)
    check("claude-code: global rules loaded", RULES in everything)
    check("claude-code: state injected by the SessionStart hook", bool(bodies) and STATE_MARK in system_text(bodies[0]))
    check("claude-code: /dev-brain:review expands the workflow", REVIEW_FLOW in everything)
    bodies = sandbox.run(mock, cmd("/dev-brain:start"), [{"text": "done"}], env)
    check("claude-code: /dev-brain:start expands the workflow", START_FLOW in json.dumps(bodies))
    check("claude-code: user-invoked workflows stay out of the skill listing",
          "dev-brain:debugging" in everything and "dev-brain:handoff" not in everything)

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
    bodies = sandbox.run(mock, cmd("check the changes"), steps, env)
    results = tool_results(bodies)
    check("claude-code: reviewer reads the diff with git", any("hello, world" in r for r in results))
    ok, rejected = write_protected(sandbox, results, 3)
    check("claude-code: reviewer cannot write without approval", ok, f"{rejected}/3 rejected")

    sandbox.big_state()
    bodies = sandbox.run(mock, cmd("hello"), [{"text": "done"}], env)
    system = system_text(bodies[0]) if bodies else ""
    check("claude-code: oversized state becomes a notice", NOTICE in system and "stale line" not in system)
    sandbox.small_state()
    sandbox.clean_repo()


def check_codex(sandbox, mock, codex):
    provider = (f'model_providers.mock={{ name = "mock", base_url = "{mock.url}/v1", '
                'wire_api = "responses", env_key = "MOCK_KEY" }')

    def cmd(prompt, *extra):
        return [codex, "exec", "--skip-git-repo-check", "-c", 'model_provider="mock"', "-c", 'model="mock"',
                "-c", provider, *extra, prompt]

    env = {"MOCK_KEY": "offline-check"}
    bodies = sandbox.run(mock, cmd("$dev-brain:review"), [{"text": "done"}], env)
    everything = json.dumps(bodies)
    check("codex: global rules loaded", RULES in everything)
    check("codex: $dev-brain:review expands the workflow", REVIEW_FLOW in everything)
    check("codex: reviewer role registered", "Read-only reviewer for correctness" in everything)
    bodies = sandbox.run(mock, cmd("$dev-brain:start"), [{"text": "done"}], env)
    check("codex: $dev-brain:start expands the workflow", START_FLOW in json.dumps(bodies))
    check("codex: state hook waits for the user's trust", STATE_MARK not in everything)
    # Trusting a hook is the user's decision; the check bypasses it only inside its own sandbox.
    bodies = sandbox.run(mock, cmd("hello", "--dangerously-bypass-hook-trust"), [{"text": "done"}], env)
    check("codex: state injected once the hook is trusted", STATE_MARK in json.dumps(bodies))
    sandbox.big_state()
    bodies = sandbox.run(mock, cmd("hello", "--dangerously-bypass-hook-trust"), [{"text": "done"}], env)
    everything = json.dumps(bodies)
    check("codex: oversized state becomes a notice", NOTICE in everything and "stale line" not in everything)
    sandbox.small_state()


def check_cursor(sandbox):
    home = Path(sandbox.env["HOME"]) / ".cursor"
    expected = ["rules/dev-brain.mdc", "agents/reviewer.md", "hooks.json", "skills/start/SKILL.md",
                "skills/review/SKILL.md", "skills/debugging/SKILL.md"]
    missing = [name for name in expected if not (home / name).exists()]
    check("cursor: files generated (not run: no headless Cursor here)", not missing, f"missing {missing}")
    agent = home / "agents" / "reviewer.md"
    check("cursor: reviewer is readonly", agent.exists() and "readonly: true" in agent.read_text())


def main():
    bins = {}
    for name, variable in (("opencode", "OPENCODE"), ("claude", "CLAUDE"), ("codex", "CODEX")):
        path = binary(name, variable)
        if path:
            bins[name] = path
    names = {"opencode": "opencode", "claude": "claude-code", "codex": "codex"}
    tools = [names[name] for name in bins] + ["cursor"]
    print(f"agents: {', '.join(tools)}")
    sandbox = Sandbox(tools, bins)
    mock = MockModel()
    try:
        if "opencode" in bins:
            check_opencode(sandbox, mock, bins["opencode"])
        if "claude" in bins:
            check_claude(sandbox, mock, bins["claude"])
        if "codex" in bins:
            check_codex(sandbox, mock, bins["codex"])
        check_cursor(sandbox)
    finally:
        mock.server.shutdown()
        shutil.rmtree(sandbox.root, ignore_errors=True)
    print("ALL PASS" if not failures else f"{len(failures)} FAILED")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
