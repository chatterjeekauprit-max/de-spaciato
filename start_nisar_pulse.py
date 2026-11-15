#!/usr/bin/env python3
"""Single-click launcher for the NISAR-PULSE local demo.

Opens the app in the default browser and serves the project folder over a small
local HTTP server so the dashboard works without any cloud dependency.
"""

from __future__ import annotations

import json
import threading
import time
import urllib.parse
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from nisar_valrix_engine import NisarValrixFusionEngine, SarEngineException

PORT = 8000


class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=str(directory), **kwargs)

    def log_message(self, format, *args):
        return

    def _send_json(self, payload, status=200):
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/health":
            self._send_json({"status": "ok", "engine": "NISAR Valrix Fusion Engine", "mode": "offline-local"})
            return

        if parsed.path == "/api/analysis":
            try:
                query = urllib.parse.parse_qs(
                    parsed.query,
                    keep_blank_values=True,
                    strict_parsing=True,
                    max_num_fields=8,
                )
                allowed_parameters = {"site", "phase", "sigma", "iono"}
                if set(query) - allowed_parameters:
                    raise ValueError("unexpected query parameter")

                def get_parameter(name, default):
                    values = query.get(name, [default])
                    if len(values) != 1:
                        raise ValueError(f"{name} must be provided once")
                    return values[0]

                site = get_parameter("site", "sundarbans")
                phase = float(get_parameter("phase", "0.0"))
                sigma = float(get_parameter("sigma", "-11.4"))
                iono = float(get_parameter("iono", "0.0"))
                engine = NisarValrixFusionEngine()
                result = engine.compute_insar_deformation(site, phase, sigma, iono)
                record = result.get("block_a", {})
                payload = {
                    "status": "ok",
                    "site": site,
                    "integrity": engine.verify_integrity(site),
                    "result": record,
                }
                self._send_json(payload)
                return
            except (SarEngineException, ValueError, TypeError, OverflowError) as exc:
                self._send_json({"status": "error", "message": str(exc)}, status=400)
                return

        return super().do_GET()


def serve(root_dir: Path, port: int) -> ThreadingHTTPServer:
    handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(root_dir), **kwargs)
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(f"NISAR-PULSE is live at http://127.0.0.1:{port}/NISAR_Pulse_App.html")
    return server


def open_browser(url: str) -> None:
    try:
        webbrowser.open_new_tab(url)
    except Exception:
        pass


def main() -> int:
    root_dir = Path(__file__).resolve().parent
    html_file = root_dir / "NISAR_Pulse_App.html"
    if not html_file.exists():
        print("Missing file: NISAR_Pulse_App.html")
        return 1

    url = f"http://127.0.0.1:{PORT}/NISAR_Pulse_App.html"
    print("Starting offline NISAR-PULSE launcher...")

    server = serve(root_dir, PORT)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    time.sleep(0.5)
    open_browser(url)

    print("Press Ctrl+C to stop the local server.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping NISAR-PULSE local server...")
        server.shutdown()
        server.server_close()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
