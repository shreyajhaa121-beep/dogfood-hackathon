import secrets
import time
import threading
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

DEMO_USERS = {
    "organizer": {
        "password": "organizer-demo",
        "role": "organizer",
    },
    "judge-a": {
        "password": "judge-a-demo",
        "role": "judge_a",
    },
    "judge-b": {
        "password": "judge-b-demo",
        "role": "judge_b",
    },
    "participant": {
        "password": "participant-demo",
        "role": "participant",
    },
}

SESSIONS = {}
SESSION_LOCK = threading.Lock()
SESSION_TTL = 60 * 60  # 1 hour


def load_fixtures():
    with FIXTURE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_role(handler):
    header = handler.headers.get("Authorization", "")

    if not header.startswith("Bearer "):
        return None

    token = header.removeprefix("Bearer ").strip()

    # Keep existing demo tokens working.
    role = TOKENS.get(token)
    if role:
        return role

    # Validate login sessions.
    with SESSION_LOCK:
        session = SESSIONS.get(token)

        if not session:
            return None

        if session["expires_at"] <= time.time():
            del SESSIONS[token]
            return None

        return session["role"]


def get_list(data, key):
    value = data.get(key, [])
    return value if isinstance(value, list) else []


class PortalHandler(BaseHTTPRequestHandler):

    def send_body(
        self,
        status,
        body,
        content_type="application/json; charset=utf-8",
    ):
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def send_json(self, status, data):
        self.send_body(
            status,
            json.dumps(data, ensure_ascii=False),
        )

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        role = get_role(self)

        try:
            data = load_fixtures()
        except (OSError, json.JSONDecodeError):
            self.send_json(
                500,
                {"error": "Could not load fixture data"},
            )
            return

        # Project gallery
        if path in ("/", "/projects"):
            projects = get_list(data, "projects")
            cards = []

            for project in projects:
                project_id = html.escape(
                    str(project.get("id", "")),
                    quote=True,
                )

                title = html.escape(
                    str(project.get("title", "Untitled project"))
                )

                summary = html.escape(
                    str(
                        project.get(
                            "summary",
                            "No description available.",
                        )
                    )
                )

                cards.append(
                    f"""
                    <article class="project-card">
                      <h3>{title}</h3>
                      <p>{summary}</p>
                      <a href="/project?id={project_id}">
                        View project details
                      </a>
                    </article>
                    """
                )

            page = (
                "<!doctype html><html lang='en'><head>"
                "<meta charset='utf-8'>"
                "<meta name='viewport' "
                "content='width=device-width, initial-scale=1.0'>"
                "<title>Dogfood Project Gallery</title>"
                "</head><body>"
                "<h1>Dogfood Hackathon Portal</h1>"
                "<h2>Project Gallery</h2>"
                + "".join(cards)
                + "</body></html>"
            )

            self.send_body(
                200,
                page,
                "text/html; charset=utf-8",
            )
            return

        # Individual project details page
        if path == "/project":
            project_id = query.get("id", [""])[0]
            projects = get_list(data, "projects")

            project = next(
                (
                    item
                    for item in projects
                    if str(item.get("id", "")) == project_id
                ),
                None,
            )

            if project is None:
                self.send_body(
                    404,
                    "<h1>Project not found</h1>"
                    "<a href='/projects'>Back to projects</a>",
                    "text/html; charset=utf-8",
                )
                return

            title = html.escape(
                str(project.get("title", "Untitled project"))
            )

            summary = html.escape(
                str(
                    project.get(
                        "summary",
                        "No description available.",
                    )
                )
            )

            project_id_text = html.escape(
                str(project.get("id", ""))
            )

            team_id = html.escape(
                str(
                    project.get(
                        "team",
                        project.get("team_id", "Not provided"),
                    )
                )
            )

            track_id = html.escape(
                str(project.get("track", "Not provided"))
            )

            repo_url = str(project.get("repo_url", "")).strip()

            if repo_url.startswith(("https://", "http://")):
                safe_repo_url = html.escape(repo_url, quote=True)

                repo_link = (
                    f"<p><a href='{safe_repo_url}' "
                    "target='_blank' rel='noopener noreferrer'>"
                    "Open project repository</a></p>"
                )
            else:
                repo_link = (
                    "<p>Repository link not provided.</p>"
                )

            page = (
                "<!doctype html><html lang='en'><head>"
                "<meta charset='utf-8'>"
                "<meta name='viewport' "
                "content='width=device-width, initial-scale=1.0'>"
                f"<title>{title}</title>"
                "</head><body>"
                "<h1>Project Details</h1>"
                f"<h2>{title}</h2>"
                f"<p>{summary}</p>"
                f"<p><strong>Project ID:</strong> "
                f"{project_id_text}</p>"
                f"<p><strong>Team ID:</strong> {team_id}</p>"
                f"<p><strong>Track ID:</strong> {track_id}</p>"
                f"{repo_link}"
                "<p><a href='/projects'>Back to projects</a></p>"
                "</body></html>"
            )

            self.send_body(
                200,
                page,
                "text/html; charset=utf-8",
            )
            return

        # Event information
        if path == "/api/event":
            self.send_json(
                200,
                {
                    "event": data.get("event", {}),
                    "tracks": data.get("tracks", []),
                },
            )
            return

        # Judge scores
        if path == "/api/judge/scores":
            if role not in ("judge_a", "judge_b"):
                self.send_json(
                    403,
                    {"error": "Judge access required"},
                )
                return

            requested_judge = query.get("judge", [None])[0]

            if requested_judge and requested_judge != role:
                self.send_json(
                    403,
                    {
                        "error":
                        "Cannot view another judge's scores"
                    },
                )
                return

            scores = get_list(data, "scores")

            own_scores = [
                score
                for score in scores
                if str(score.get("judge_id", "")).lower() == role
                or str(score.get("judge", "")).lower() == role
            ]

            self.send_json(200, {"scores": own_scores})
            return

        # Organizer CSV export
        if path == "/api/export.csv":
            if role != "organizer":
                self.send_json(
                    403,
                    {"error": "Organizer access required"},
                )
                return

            projects = get_list(data, "projects")
            output = io.StringIO()
            writer = csv.writer(output)

            writer.writerow(
                ["project_id", "title", "team_id"]
            )

            for project in projects:
                writer.writerow([
                    project.get("id", ""),
                    project.get("title", ""),
                    project.get(
                        "team",
                        project.get("team_id", ""),
                    ),
                ])

            self.send_body(
                200,
                output.getvalue(),
                "text/csv; charset=utf-8",
            )
            return

        self.send_json(404, {"error": "Route not found"})

    def do_POST(self):
        path = urlparse(self.path).path

        # Login
        if path == "/login":
            try:
                length = int(
                    self.headers.get("Content-Length", "0")
                )
                body = json.loads(
                    self.rfile.read(length).decode("utf-8")
                )
            except (ValueError, json.JSONDecodeError):
                self.send_json(
                    400,
                    {"error": "Invalid JSON"},
                )
                return

            if not isinstance(body, dict):
                self.send_json(
                    400,
                    {"error": "Invalid request body"},
                )
                return

            username = body.get("username", "")
            password = body.get("password", "")

            user = DEMO_USERS.get(username)

            if not user or user["password"] != password:
                self.send_json(
                    401,
                    {"error": "Invalid username or password"},
                )
                return

            token = secrets.token_urlsafe(32)

            with SESSION_LOCK:
                SESSIONS[token] = {
                    "role": user["role"],
                    "expires_at": time.time() + SESSION_TTL,
                }

            self.send_json(
                200,
                {
                    "token": token,
                    "role": user["role"],
                    "expires_in": SESSION_TTL,
                },
            )
            return

        # Logout
        if path == "/logout":
            header = self.headers.get("Authorization", "")

            if not header.startswith("Bearer "):
                self.send_json(
                    401,
                    {"error": "Authentication required"},
                )
                return

            token = header.removeprefix("Bearer ").strip()

            with SESSION_LOCK:
                session = SESSIONS.get(token)

                if (
                    not session
                    or session["expires_at"] <= time.time()
                ):
                    SESSIONS.pop(token, None)
                    self.send_json(
                        401,
                        {"error": "Invalid or expired session"},
                    )
                    return

                del SESSIONS[token]

            self.send_json(
                200,
                {"message": "Logged out successfully"},
            )
            return

        # New project submission
        if path == "/projects/new":
            role = get_role(self)

            if role is None:
                self.send_json(
                    401,
                    {"error": "Authentication required"},
                )
                return

            if role != "participant":
                self.send_json(
                    403,
                    {"error": "Participant access required"},
                )
                return

            # The supplied fixture's submission deadline is in the past.
            self.send_json(
                409,
                {"error": "Submission period is closed"},
            )
            return

        # Unknown POST route
        self.send_json(
            404,
            {"error": "Route not found"},
        )


if __name__ == "__main__":
    server = ThreadingHTTPServer(
        ("0.0.0.0", 8080),
        PortalHandler,
    )

    print("Dogfood portal running on port 8080")
    server.serve_forever()
