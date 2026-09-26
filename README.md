Dogfood Hackathon Portal

A self-hostable hackathon submission and judging portal built for Dogfood Hackathon 2026.

Overview

The Dogfood Hackathon Portal provides a public project gallery, role-protected judging scores, and organizer CSV export.

The portal uses fixture data and is designed to run locally with Docker Compose without external API calls.

Features

- Public project gallery populated from "fixtures.json"
- Submission endpoint that refuses submissions after the event deadline
- Judge-only access to judging scores
- Protection against judges viewing another judge's scores
- Participant access blocked from judge scores
- Organizer-only CSV export
- Docker Compose setup for local deployment

Technology

- Python 3 standard library
- Docker and Docker Compose
- JSON fixture data
- HTML

Requirements

- Docker with Docker Compose
- Python 3 for running the acceptance checker

Run the Portal

From the repository root, start the portal using:

docker compose up --build

Open the project gallery in your browser:

"http://localhost:8080/projects"

To stop the portal, press "Ctrl+C" in the terminal running Docker Compose.

Run Acceptance Checks

Keep the portal running and open a second terminal.

Run the acceptance checker and save its output:

python3 run.py .dogfood.toml > acceptance-report.txt

View the report:

cat acceptance-report.txt

The committed acceptance report records the results for the configured T1 and T2 tiers.

Project Files

- "server.py" — HTTP server and portal routes
- "fixtures.json" — Event and project fixture data
- ".dogfood.toml" — Checker configuration, routes, and authentication headers
- "Dockerfile" — Container image definition
- "docker-compose.yml" — Local portal startup configuration
- "run.py" — Acceptance checker supplied for the event
- "acceptance-report.txt" — Recorded acceptance results
- "index.html" — Frontend HTML
- "style.css" — Frontend styles
- "app.js" — Frontend JavaScript
- "LICENSE" — MIT License

Acceptance Results

The acceptance checker reported that all seven configured T1 and T2 checks passed. See "acceptance-report.txt" for the recorded results.

License

This project is licensed under the MIT License. See "LICENSE" for details.
