from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json
import mimetypes
import sys
import traceback
from urllib.parse import parse_qs, urlparse

from omniquantai.exporters import render_investment_committee_memo
from omniquantai.orchestrator import OmniQuantOrchestrator
from omniquantai.storage import RunStore


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
DATA_DIR = ROOT / "data"


store = RunStore(DATA_DIR / "runs.json")
orchestrator = OmniQuantOrchestrator(store=store)


class OmniQuantHandler(SimpleHTTPRequestHandler):
    server_version = "OmniQuantAI/0.1"

    def log_message(self, fmt, *args):
        sys.stdout.write("%s - %s\n" % (self.address_string(), fmt % args))

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            if parsed.path == "/":
                self._send_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
                return

            if parsed.path == "/api/memo":
                params = parse_qs(parsed.query)
                run_id = params.get("run_id", [None])[0]
                run = orchestrator.get_run(run_id)
                memo = render_investment_committee_memo(run)
                filename = f"omniquantai-{run['asset']['ticker'].lower()}-memo.md"
                self._send_text(memo, "text/markdown; charset=utf-8", filename)
                return

            if parsed.path.startswith("/static/"):
                relative = parsed.path.removeprefix("/static/")
                target = (STATIC_DIR / relative).resolve()
                if STATIC_DIR in target.parents and target.exists() and target.is_file():
                    content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
                    self._send_file(target, content_type)
                    return

            self._send_json({"error": "Not found"}, status=404)
        except Exception as exc:
            traceback.print_exc()
            self._send_json({"error": str(exc)}, status=500)

    def do_POST(self):
        try:
            body = self._read_json()
            if self.path == "/api/research":
                query = body.get("query", "").strip()
                if not query:
                    self._send_json({"error": "A ticker or company question is required."}, status=400)
                    return
                portfolio_context = body.get("portfolio_context", {})
                result = orchestrator.run_research(query, portfolio_context=portfolio_context)
                self._send_json(result)
                return

            if self.path == "/api/scenario":
                scenario = body.get("scenario", "").strip()
                run_id = body.get("run_id")
                if not scenario:
                    self._send_json({"error": "A scenario question is required."}, status=400)
                    return
                result = orchestrator.run_scenario(scenario=scenario, run_id=run_id)
                self._send_json(result)
                return

            self._send_json({"error": "Not found"}, status=404)
        except Exception as exc:
            traceback.print_exc()
            self._send_json({"error": str(exc)}, status=500)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw or "{}")

    def _send_file(self, path, content_type):
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_text(self, text, content_type, filename=None):
        data = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload, status=200):
        data = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), OmniQuantHandler)
    print(f"OmniQuantAI MVP running at http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")


if __name__ == "__main__":
    main()
