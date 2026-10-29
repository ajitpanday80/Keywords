import csv
import io
import json
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from urllib.parse import parse_qs, urlparse

from . import pipeline
from .demo import DemoLLM
from .llm import OpenRouterLLM
from .models import Business

JOBS: dict[str, dict] = {}


def _run_job(jid: str, p: dict) -> None:
    job = JOBS[jid]
    try:
        llm = DemoLLM() if p.get("demo") else OpenRouterLLM(p.get("model") or None,
                                                            p.get("api_key") or None)
        biz = Business(description=p["business"], audience=p.get("audience", ""),
                       market=p.get("market") or "US, English",
                       site_strength=p.get("site_strength", "new"))
        clamp = lambda v, lo, hi, d: max(lo, min(hi, int(v or d)))
        job["result"] = pipeline.run(
            llm, biz, clamp(p.get("intents"), 1, 20, 8), clamp(p.get("seo"), 1, 30, 10),
            clamp(p.get("geo"), 1, 20, 6),
            progress=lambda m, d, t: job.update(message=m, done=d, total=t))
        job["status"] = "done"
    except Exception as e:  # surface any failure to the UI
        job.update(status="error", error=str(e))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json", extra=None):
        data = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/":
            html = resources.files("kwintent").joinpath("index.html").read_bytes()
            return self._send(200, html, "text/html; charset=utf-8")
        parts = u.path.strip("/").split("/")
        if parts[:2] == ["api", "jobs"] and len(parts) >= 3 and parts[2] in JOBS:
            job = JOBS[parts[2]]
            if len(parts) == 3:
                return self._send(200, json.dumps(job))
            kind = parse_qs(u.query).get("kind", ["seo"])[0]
            rows = job.get("result", {}).get("seo_keywords" if kind == "seo" else "geo_prompts", [])
            buf = io.StringIO()
            if rows:
                w = csv.DictWriter(buf, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)
            return self._send(200, buf.getvalue(), "text/csv",
                              {"Content-Disposition": f"attachment; filename={kind}.csv"})
        self._send(404, '{"error":"not found"}')

    def do_POST(self):
        if self.path != "/api/research":
            return self._send(404, '{"error":"not found"}')
        try:
            p = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            if not str(p.get("business", "")).strip():
                return self._send(400, '{"error":"Describe the business first."}')
        except ValueError:
            return self._send(400, '{"error":"bad json"}')
        jid = uuid.uuid4().hex[:12]
        JOBS[jid] = {"status": "running", "message": "Starting", "done": 0, "total": 1}
        threading.Thread(target=_run_job, args=(jid, p), daemon=True).start()
        self._send(200, json.dumps({"id": jid}))


def serve(host="127.0.0.1", port=8000):
    print(f"kwintent UI on http://{host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
