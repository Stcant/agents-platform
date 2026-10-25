"""Local model endpoint that records requests and replays scripted replies.

Speaks the three wire formats the supported agents use:
- OpenAI chat completions (`/chat/completions`): OpenCode
- Anthropic messages (`/messages`): Claude Code
- OpenAI responses (`/responses`): Codex CLI

Requests that offer tools are agent-loop calls: each one pops the next matching
scripted step, either {"tool": name, "args": {...}} or {"text": "..."}, optionally
limited with "when" / "unless" text. Other requests (titles, summaries) get a fixed
text. Nothing reaches a real provider.
"""
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class MockModel:
    def __init__(self):
        self.steps, self.requests, self.lock = [], [], threading.Lock()
        mock = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *args):
                pass

            def do_GET(self):
                self._json({"data": [{"id": "mock", "object": "model", "type": "model", "display_name": "Mock"}],
                            "models": [], "has_more": False})

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers.get("content-length", 0))) or b"{}")
                path = self.path.split("?")[0]
                if path.endswith("/count_tokens"):
                    return self._json({"input_tokens": 1})
                with mock.lock:
                    mock.requests.append({"path": path, "body": body})
                    step = mock.next_step(body)
                if path.endswith("/messages"):
                    self._anthropic(body, step)
                elif path.endswith("/responses"):
                    self._responses(step)
                else:
                    self._chat(step)

            def _json(self, payload):
                data = json.dumps(payload).encode()
                self.send_response(200)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _sse(self, events):
                self.send_response(200)
                self.send_header("content-type", "text/event-stream")
                self.send_header("cache-control", "no-cache")
                self.send_header("connection", "close")
                self.end_headers()
                for name, data in events:
                    prefix = f"event: {name}\n" if name else ""
                    self.wfile.write(f"{prefix}data: {json.dumps(data)}\n\n".encode())
                self.wfile.flush()
                self.close_connection = True

            def _chat(self, step):
                call_id = f"call_{len(mock.requests)}"
                if "tool" in step:
                    delta = {"role": "assistant", "tool_calls": [{"index": 0, "id": call_id, "type": "function",
                             "function": {"name": step["tool"], "arguments": json.dumps(step["args"])}}]}
                    finish = "tool_calls"
                else:
                    delta, finish = {"role": "assistant", "content": step["text"]}, "stop"
                base = {"id": "c", "object": "chat.completion.chunk", "created": 0, "model": "mock"}
                self._sse([
                    (None, {**base, "choices": [{"index": 0, "delta": delta, "finish_reason": None}]}),
                    (None, {**base, "choices": [{"index": 0, "delta": {}, "finish_reason": finish}],
                            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}}),
                ])
                self.wfile.write(b"data: [DONE]\n\n")

            def _anthropic(self, body, step):
                if "tool" in step:
                    block = {"type": "tool_use", "id": f"toolu_{len(mock.requests)}", "name": step["tool"], "input": {}}
                    delta = {"type": "input_json_delta", "partial_json": json.dumps(step["args"])}
                    stop = "tool_use"
                else:
                    block, delta, stop = {"type": "text", "text": ""}, {"type": "text_delta", "text": step["text"]}, "end_turn"
                usage = {"input_tokens": 1, "output_tokens": 1}
                message = {"id": "msg_mock", "type": "message", "role": "assistant", "model": body.get("model", "mock"),
                           "content": [], "stop_reason": None, "stop_sequence": None, "usage": usage}
                if not body.get("stream"):
                    content = dict(block, input=step["args"]) if "tool" in step else {"type": "text", "text": step["text"]}
                    return self._json({**message, "content": [content], "stop_reason": stop})
                self._sse([
                    ("message_start", {"type": "message_start", "message": message}),
                    ("content_block_start", {"type": "content_block_start", "index": 0, "content_block": block}),
                    ("content_block_delta", {"type": "content_block_delta", "index": 0, "delta": delta}),
                    ("content_block_stop", {"type": "content_block_stop", "index": 0}),
                    ("message_delta", {"type": "message_delta", "delta": {"stop_reason": stop, "stop_sequence": None},
                                       "usage": {"output_tokens": 1}}),
                    ("message_stop", {"type": "message_stop"}),
                ])

            def _responses(self, step):
                n = len(mock.requests)
                if "tool" in step:
                    item = {"type": "function_call", "id": f"fc_{n}", "call_id": f"call_{n}", "name": step["tool"],
                            "arguments": json.dumps(step["args"]), "status": "completed"}
                    if "namespace" in step:
                        item["namespace"] = step["namespace"]
                else:
                    item = {"type": "message", "id": f"msg_{n}", "role": "assistant", "status": "completed",
                            "content": [{"type": "output_text", "text": step["text"], "annotations": []}]}
                usage = {"input_tokens": 1, "input_tokens_details": {"cached_tokens": 0}, "output_tokens": 1,
                         "output_tokens_details": {"reasoning_tokens": 0}, "total_tokens": 2}
                response = {"id": f"resp_{n}", "object": "response", "status": "in_progress", "model": "mock", "output": []}
                self._sse([
                    ("response.created", {"type": "response.created", "response": response}),
                    ("response.output_item.added", {"type": "response.output_item.added", "output_index": 0,
                                                    "item": dict(item, status="in_progress")}),
                    ("response.output_item.done", {"type": "response.output_item.done", "output_index": 0, "item": item}),
                    ("response.completed", {"type": "response.completed",
                                            "response": dict(response, status="completed", output=[item], usage=usage)}),
                ])

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_port}"

    def next_step(self, body):
        """First scripted step whose optional `when` / `unless` text matches this request.

        Concurrent agents (a parent and its subagent) can then follow separate lanes.
        """
        if not body.get("tools"):
            return {"text": "ok"}
        text = json.dumps(body)
        for index, step in enumerate(self.steps):
            if step.get("when", "") in text and not (step.get("unless") and step["unless"] in text):
                step = self.steps.pop(index)
                found = re.search(r'agent_id\\*":\\*"([^"\\]+)', text)
                if found and "args" in step:  # lets a script wait on the subagent it spawned
                    step = dict(step, args=json.loads(json.dumps(step["args"]).replace("$AGENT_ID", found.group(1))))
                return step
        return {"text": "ok"}

    def script(self, steps):
        with self.lock:
            self.steps, self.requests = list(steps), []

    def agent_calls(self):
        return [r["body"] for r in self.requests if r["body"].get("tools")]


if __name__ == "__main__":
    import sys
    import time

    mock = MockModel()
    log = sys.argv[1] if len(sys.argv) > 1 else None
    print(mock.url, flush=True)
    seen = 0
    while True:
        time.sleep(0.5)
        if log and len(mock.requests) > seen:
            with open(log, "a", encoding="utf-8") as handle:
                for request in mock.requests[seen:]:
                    handle.write(json.dumps(request) + "\n")
            seen = len(mock.requests)
