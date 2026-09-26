from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent
FIXTURE_FILE = BASE_DIR / "fixtures.json"


def load_fixtures():
    with FIXTURE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


class PortalHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/projects":
            try:
                data = load_fixtures()

                response = {
                    "event": data.get("event", {}),
                    "projects": data.get("projects", [])
                }

                body = json.dumps(response).encode("utf-8")

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            except (OSError, json.JSONDecodeError):
                self.send_error(500, "Could not load fixture data")

        else:
            self.send_error(404, "Route not found")


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), PortalHandler)
    print("Dogfood portal running on port 8080")
    server.serve_forever()
