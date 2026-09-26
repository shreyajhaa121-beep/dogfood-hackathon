from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import csv
import io
import json
import html

BASE_DIR = Path(__file__).resolve().parent
FIXTURE_FILE = BASE_DIR / "fixtures.json"

TOKENS = {
    "organizer-demo": "organizer",
    "judge-a-demo": "judge_a",
    "judge-b-demo": "judge_b",
    "participant-demo": "participant",
}


def load_fixtures():
    with FIXTURE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_role(handler):
    header = handler.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        token = header.removeprefix("Bearer ").strip()
        return TOKENS.get(token)
    return None


def get_list(data, key):
    value = data.get(key, [])
    return value if isinstance(value, list) else []


class PortalHandler(BaseHTTPRequestHandler):
    def send_body(self, status, body, content_type="application/json; charset=utf-8"):
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def send_json(self, status, data):
        self.send_body(status, json.dumps(data, ensure_ascii=False))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        role = get_role(self)

        try:
            data = load_fixtures()
        except (OSError, json.JSONDecodeError):
            self.send_json(500, {"error": "Could not load fixture data"})
            return

        if path in ("/", "/projects"):
            projects = get_list(data, "projects")
            cards = []

            for project in projects:
                title = html.escape(str(project.get("title", "Untitled project")))
                cards.append(f"<li>{title}</li>")

            page = (
                "<!doctype html><html><head><meta charset='utf-8'>"
                "<title>Dogfood Project Gallery</title></head><body>"
                "<h1>Dogfood Hackathon Portal</h1>"
                "<h2>Project Gallery</h2><ul>"
                + "".join(cards)
                + "</ul></body></html>"
            )
            self.send_body(200, page, "text/html; charset=utf-8")
            return

        if path == "/api/judge/scores":
            if role not in ("judge_a", "judge_b"):
                self.send_json(403, {"error": "Judge access required"})
                return

            requested_judge = query.get("judge", [None])[0]

            if requested_judge == "judge_a" and role != "judge_a":
                self.send_json(403, {"error": "Cannot view another judge's scores"})
                return

            scores = get_list(data, "scores")
            own_scores = [
                score for score in scores
                if str(score.get("judge_id", "")).lower() == role
                or str(score.get("judge", "")).lower() == role
            ]

            self.send_json(200, {"scores": own_scores})
            return

        if path == "/api/export.csv":
            if role != "organizer":
                self.send_json(403, {"error": "Organizer access required"})
                return

            projects = get_list(data, "projects")
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["project_id", "title", "team_id"])

            for project in projects:
                writer.writerow([
                    project.get("id", ""),
                    project.get("title", ""),
                    project.get("team_id", ""),
                ])

            self.send_body(200, output.getvalue(), "text/csv; charset=utf-8")
            return

        self.send_json(404, {"error": "Route not found"})

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/projects/new":
            role = get_role(self)

            if role != "participant":
                self.send_json(401, {"error": "Participant authentication required"})
                return

            # The supplied fixture's submission deadline is in the past.
            self.send_json(409, {"error": "Submission period is closed"})
            return

        self.send_json(404, {"error": "Route not found"})


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8080), PortalHandler)
    print("Dogfood portal running on port 8080")
    server.serve_forever()
