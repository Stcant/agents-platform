#!/usr/bin/env python3
"""Zero-token check of the installed harness against a real OpenCode binary.

A local OpenAI-compatible mock replaces the model: it replays scripted tool calls
and records every request OpenCode sends. Nothing reaches a real provider, so the
check costs no tokens. It verifies what the kit controls:

- the saved state reaches the main session and not subagent sessions;
- an oversized state is replaced by a short notice;
- the reviewer can read the diff with git but cannot write files.

It does not judge model behavior; use evals/scenarios/ for that.

Usage: python3 evals/offline/check.py        (needs `opencode` V2, git, bash)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

KIT = Path(__file__).resolve().parents[2]
OPENCODE = os.environ.get("OPENCODE", "opencode")
STATE = """# State — fixture
Updated: 2026-01-01 · Branch: main

## Goal
Keep the greeting stable — acceptance: app.txt says hello.

## Next (max 3)
1. Review the pending change.
"""


class Mock:
    """Scripted chat-completions endpoint; requests without tools (titles) get plain text."""

    def __init__(self):
        self.steps, self.requests, self.lock = [], [], threading.Lock()
        mock = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["content-length"])))
                with mock.lock:
                    mock.requests.append(body)
                    step = mock.steps.pop(0) if body.get("tools") and mock.steps else {"text": "ok"}
                if "tool" in step:
                    call = {"index": 0, "id": f"call_{len(mock.requests)}", "type": "function",
                            "function": {"name": step["tool"], "arguments": json.dumps(step["args"])}}
                    deltas, finish = [{"role": "assistant", "tool_calls": [call]}], "tool_calls"
                else:
                    deltas, finish = [{"role": "assistant", "content": step["text"]}], "stop"
                chunks = [{"choices": [{"index": 0, "delta": d, "finish_reason": None}]} for d in deltas]
                chunks.append({"choices": [{"index": 0, "delta": {}, "finish_reason": finish}],
                               "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}})
                self.send_response(200)
                self.send_header("content-type", "text/event-stream")
                self.end_headers()
                for chunk in chunks:
                    chunk.update({"id": "c", "object": "chat.completion.chunk", "created": 0, "model": "mock"})
                    self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
                self.wfile.write(b"data: [DONE]\n\n")

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_port}/v1"


def system_text(request):
    return "\n".join(m["content"] for m in request["messages"]
                     if m["role"] == "system" and isinstance(m["content"], str))


def tool_results(requests):
    """Tool outputs fed back to the model, once per tool call, in order."""
    results = {}
    for request in requests:
        for message in request["messages"]:
            if message["role"] == "tool":
                content = message["content"]
                results.setdefault(message.get("tool_call_id"),
                                   content if isinstance(content, str) else json.dumps(content))
    return list(results.values())


def run(env, repo, mock, steps, prompt="check"):
    """One `opencode run` in the fixture; returns the agent-loop requests (those offering tools)."""
    mock.steps, mock.requests = list(steps), []
    # stdin must be closed: `opencode run` reads piped stdin and waits for EOF otherwise.
    # PWD must match cwd: OpenCode resolves the project from it.
    subprocess.run([OPENCODE, "run", "--standalone", "-m", "mock/mock", prompt], cwd=repo,
                   env=dict(env, PWD=str(repo)), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, timeout=180)
    requests = [r for r in mock.requests if r.get("tools")]
    if not requests:
        raise SystemExit("FAIL  opencode sent no request to the mock model")
    return requests


def main():
    if not shutil.which(OPENCODE):
        raise SystemExit(f"`{OPENCODE}` not found; set OPENCODE to the V2 binary")
    mock = Mock()
    sandbox = Path(tempfile.mkdtemp(prefix="dev-brain-offline-"))
    # Fully offline: the mock is the only provider, so skip the model catalog download.
    env = dict(os.environ, HOME=str(sandbox / "home"), OPENCODE_DISABLE_MODELS_FETCH="1",
               OPENCODE_DISABLE_FREE_MODELS="1")
    for name in ("CONFIG", "DATA", "STATE", "CACHE"):
        env[f"XDG_{name}_HOME"] = str(sandbox / name.lower())
    subprocess.run([str(KIT / "install.sh")], env=env, check=True, stdout=subprocess.DEVNULL)
    config_file = sandbox / "config" / "opencode" / "opencode.json"
    config = json.loads(config_file.read_text())
    config["model"] = "mock/mock"
    config["providers"] = {"mock": {
        "name": "Mock", "package": "@opencode/ai/providers/openai-compatible",
        "settings": {"baseURL": mock.url},
        "models": {"mock": {"name": "Mock", "capabilities": {"tools": True, "input": ["text"], "output": ["text"]},
                            "limit": {"context": 200000, "output": 8000}}}}}
    config_file.write_text(json.dumps(config, indent=2))

    repo = sandbox / "repo"
    (repo / ".dev-brain").mkdir(parents=True)
    git = ["git", "-c", "user.name=check", "-c", "user.email=check@example.invalid"]
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    (repo / "app.txt").write_text("hello\n")
    subprocess.run(git + ["add", "app.txt"], cwd=repo, check=True)
    subprocess.run(git + ["commit", "-qm", "fixture"], cwd=repo, check=True)
    (repo / "app.txt").write_text("hello, world\n")
    (repo / ".dev-brain" / "STATE.md").write_text(STATE)

    failures = []

    def check(name, ok, detail=""):
        print(f"{'PASS' if ok else 'FAIL'}  {name}{f' — {detail}' if detail and not ok else ''}")
        if not ok:
            failures.append(name)

    reviewer_steps = [
        {"tool": "subagent", "args": {"agent": "reviewer", "description": "review", "prompt": "Review all changes."}},
        {"tool": "shell", "args": {"command": "git diff HEAD"}},
        {"tool": "shell", "args": {"command": "git diff HEAD > leak.txt"}},
        {"tool": "shell", "args": {"command": "git diff HEAD --output=leak.txt"}},
        {"tool": "shell", "args": {"command": "git status; rm app.txt"}},
        {"text": "no findings"},
        {"text": "done"},
    ]
    requests = run(env, repo, mock, reviewer_steps)
    main_calls = [r for r in requests if any(t["function"]["name"] == "edit" for t in r["tools"])]
    child_calls = [r for r in requests if r not in main_calls]
    results = tool_results(requests)
    check("state injected in the main session", bool(main_calls) and all("<dev-brain-state" in system_text(r) for r in main_calls))
    check("state not injected in the subagent", bool(child_calls) and not any("<dev-brain-state" in system_text(r) for r in child_calls))
    check("reviewer reads the diff with git", any("hello, world" in r for r in results))
    rejected = sum("permission.rejected" in r for r in results)
    check("reviewer cannot redirect, --output or rm",
          rejected == 3 and not (repo / "leak.txt").exists() and (repo / "app.txt").exists(),
          f"{rejected}/3 rejected, leak.txt={(repo / 'leak.txt').exists()}, app.txt={(repo / 'app.txt').exists()}")
    print(f"info  main-session system prompt: {len(system_text(main_calls[0]))} chars; "
          f"subagent: {len(system_text(child_calls[0]))} chars" if main_calls and child_calls else "info  no sizes")

    (repo / ".dev-brain" / "STATE.md").write_text(STATE + "- stale line\n" * 300)
    requests = run(env, repo, mock, [{"text": "done"}])
    system = system_text(requests[0])
    check("oversized state replaced by a notice", "over the 3000-character budget" in system and "stale line" not in system)

    shutil.rmtree(sandbox, ignore_errors=True)
    print("ALL PASS" if not failures else f"{len(failures)} FAILED")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
