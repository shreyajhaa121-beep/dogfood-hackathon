# Dogfood Hackathon Portal

A self-hostable hackathon submission and judging portal built for Dogfood Hackathon 2026.

## Overview

Dogfood Hackathon Portal is a lightweight platform for managing hackathon project submissions and judging. It provides a public project gallery, individual project details, role-protected judging scores, and organizer CSV export.

The portal runs locally using Docker Compose and uses fixture data without requiring external API calls.

A GitHub Pages frontend is also included to display the public project gallery and individual project details.

## Features

- Public project gallery powered by `fixtures.json`
- Individual project details pages with project, team, and track information
- Links to project repositories when available
- Submission endpoint that rejects submissions after the event deadline
- Judge-only access to judging scores
- Protection against judges viewing other judges' scores
- Participant access blocked from judge scores
- Organizer-only CSV export
- Docker Compose setup for local deployment
- GitHub Pages frontend for browsing projects and their details

## Technology

- Python 3 standard library
- Docker and Docker Compose
- JSON fixture data
- HTML
- CSS
- JavaScript

## Requirements

- Docker with Docker Compose
- Python 3 for running the acceptance checker and automated tests

## Run the Portal

From the repository root, start the portal using:

```bash
docker compose up --build
```

Open the project gallery in your browser:

http://localhost:8080/projects

To stop the portal, press `Ctrl+C` in the terminal running Docker Compose.

## Run Acceptance Checks

Keep the portal running and open a second terminal.

Run the acceptance checker and save its output:

```bash
python3 run.py .dogfood.toml > acceptance-report.txt
```

View the report:

```bash
cat acceptance-report.txt
```

The committed acceptance report records the results for the configured T1 and T2 tiers.

## Automated Tests

Run the automated portal tests from the repository root:

```bash
python3 -m unittest discover -s test -v
```

The latest test run completed successfully with all 9 tests passing.

## Project Files

- `server.py` — HTTP server and portal routes
- `fixtures.json` — Event and project fixture data
- `.dogfood.toml` — Checker configuration, routes, and authentication headers
- `Dockerfile` — Container image definition
- `docker-compose.yml` — Local portal startup configuration
- `run.py` — Acceptance checker supplied for the event
- `acceptance-report.txt` — Recorded acceptance results
- `index.html` — GitHub Pages project gallery
- `style.css` — Frontend styles
- `app.js` — Frontend logic for loading projects and displaying details links
- `project-details.html` — Individual project details page for GitHub Pages
- `test/test_server.py` — Automated portal tests
- `LICENSE` — MIT License

## Acceptance Results

The acceptance checker reported that all seven configured T1 and T2 checks passed. See `acceptance-report.txt` for the recorded results.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
