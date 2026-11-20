"""Local model endpoint that records requests and replays scripted replies.

Speaks two wire formats: Anthropic Messages (Claude Code, and Copilot CLI configured
with its Anthropic provider) and OpenAI Responses (Codex CLI, `/responses`).

Requests that offer tools are agent-loop calls: each one pops the first scripted step
whose optional "when" / "unless" text matches the request, either
{"tool": name, "args": {...}} or {"text": "..."}. Other requests get a fixed text.
Nothing reaches a real provider.
"""
import json
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
                self._json({"data": [], "has_more": False})

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers.get("content-length", 0))) or b"{}")
                path = self.path.split("?")[0]
                if path.endswith("/count_tokens"):
                    return self._json({"input_tokens": 1})
                with mock.lock:
                    mock.requests.append(body)
                    step = mock.next_step(body)
                (self._responses if path.endswith("/responses") else self._reply)(body, step)

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
                self.send_header("connection", "close")
                self.end_headers()
                for name, data in events:
                    self.wfile.write(f"event: {name}\ndata: {json.dumps(data)}\n\n".encode())
                self.wfile.flush()
                self.close_connection = True

            def _responses(self, body, step):
                n = len(mock.requests)
                if "tool" in step:
                    item = {"type": "function_call", "id": f"fc_{n}", "call_id": f"call_{n}", "name": step["tool"],
                            "arguments": json.dumps(step["args"]), "status": "completed"}
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

            def _reply(self, body, step):
                if "tool" in step:
                    block = {"type": "tool_use", "id": f"toolu_{len(mock.requests)}", "name": step["tool"], "input": {}}
                    delta = {"type": "input_json_delta", "partial_json": json.dumps(step["args"])}
                    stop = "tool_use"
                else:
                    block, delta, stop = {"type": "text", "text": ""}, {"type": "text_delta", "text": step["text"]}, "end_turn"
                message = {"id": "msg_mock", "type": "message", "role": "assistant", "model": body.get("model", "mock"),
                           "content": [], "stop_reason": None, "stop_sequence": None,
                           "usage": {"input_tokens": 1, "output_tokens": 1}}
                if not body.get("stream"):
                    content = dict(block, input=step["args"]) if "tool" in step else {"type": "text", "text": step["text"]}
                    return self._json({**message, "content": [content], "stop_reason": stop})
                events = [
                    ("message_start", {"type": "message_start", "message": message}),
                    ("content_block_start", {"type": "content_block_start", "index": 0, "content_block": block}),
                    ("content_block_delta", {"type": "content_block_delta", "index": 0, "delta": delta}),
                    ("content_block_stop", {"type": "content_block_stop", "index": 0}),
                    ("message_delta", {"type": "message_delta", "delta": {"stop_reason": stop, "stop_sequence": None},
                                       "usage": {"output_tokens": 1}}),
                    ("message_stop", {"type": "message_stop"}),
                ]
                self._sse(events)

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_port}"

    def next_step(self, body):
        if not body.get("tools"):
            return {"text": "ok"}
        text = json.dumps(body)
        for index, step in enumerate(self.steps):
            if step.get("when", "") in text and not (step.get("unless") and step["unless"] in text):
                return self.steps.pop(index)
        return {"text": "ok"}

    def script(self, steps):
        with self.lock:
            self.steps, self.requests = list(steps), []

    def agent_calls(self):
        return [body for body in self.requests if body.get("tools")]
