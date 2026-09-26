Architecture — Dogfood Hackathon Portal

1. System Overview

The Dogfood Hackathon Portal is a self-hostable web application for displaying hackathon projects, protecting judging scores, and allowing organizers to export project data.

The application uses Python's standard library and JSON fixture data. It runs locally through Docker Compose and does not require external API calls during normal operation.

2. Main Components

Web Server — "server.py"

The Python HTTP server handles incoming requests and provides the portal's routes.

Its responsibilities include:

- Serving the public project gallery
- Loading project data from "fixtures.json"
- Checking authorization headers for protected routes
- Blocking submissions after the event deadline
- Returning judge score data
- Generating CSV exports for organizers

Fixture Data — "fixtures.json"

The fixture file contains the event data used by the portal, including project information and judging data.

The server reads this file to populate the gallery and provide data for the API routes.

Frontend Files

- "index.html" — HTML frontend page
- "style.css" — Frontend styling
- "app.js" — Frontend JavaScript

The Python server currently generates the HTML response for the "/projects" gallery route.

Docker Configuration

- "Dockerfile" defines the Python container image.
- "docker-compose.yml" builds and starts the portal container.
- The portal listens on port "8080".

3. Request Flow

The portal handles requests in the following order:

1. A browser or acceptance checker sends an HTTP request.
2. Docker forwards the request to the Python server.
3. "server.py" identifies the requested route.
4. The route handler checks access permissions when required.
5. The server reads the necessary information from "fixtures.json".
6. The server sends the response to the browser or checker.

Request Flow Summary

Browser or Acceptance Checker
↓
Docker Container
↓
Python Server ("server.py")
↓
Route Handler
↓
Gallery / Judge Scores / CSV Export
↓
Fixture Data ("fixtures.json")

4. Routes

Route| Method| Access
"/projects"| GET| Public
"/projects/new"| POST| Participant authentication required; closed event submissions are rejected
"/api/judge/scores"| GET| Judge authentication required
"/api/judge/scores?judge=judge_a"| GET| Judge A can access their own scores; other roles are denied
"/api/export.csv"| GET| Organizer authentication required

The route paths are configured in ".dogfood.toml" for the acceptance checker.

5. Authentication and Authorization

The server checks the "Authorization" request header for protected routes.

The configured demo roles are:

- Organizer
- Judge A
- Judge B
- Participant

The server restricts judge score access to authenticated judges and prevents Judge B from requesting Judge A's scores. Participants cannot access judge scores. CSV export is restricted to the organizer role.

6. Submission Deadline

The submission route rejects requests because the supplied event fixture represents a closed submission period.

The acceptance checker verifies that a submission request receives a client error response.

7. Local Deployment

The portal is built and started using Docker Compose:

docker compose up --build

The gallery is available at:

"http://localhost:8080/projects"

The application uses the provided fixture data and does not call external APIs.

8. Acceptance Testing

The event-provided acceptance checker is run with:

python3 run.py .dogfood.toml > acceptance-report.txt

The recorded report showed all seven configured T1 and T2 checks passing. The report is committed in "acceptance-report.txt".
