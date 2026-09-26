# Architecture Documentation

## 1. Project Overview

This project is a local hackathon portal designed to demonstrate a project gallery, participant submission handling, judge score access control, and organizer CSV export.

The application runs locally using Docker Compose and does not require cloud services or external APIs.

The main components are:

- Python HTTP server
- Docker container
- Docker Compose configuration
- Project fixture data
- Authentication and access-control checks
- Acceptance checker

## 2. System Components

### 2.1 Python Server

File: `server.py`

The Python server handles incoming HTTP requests.

Its responsibilities include:

- Serving the project gallery
- Handling project submission requests
- Checking authentication for protected routes
- Restricting access to judging data
- Providing organizer CSV export
- Returning HTTP responses

The server uses Python's standard library.

### 2.2 Fixture Data

File: `fixtures.json`

The fixture file contains sample project data used by the portal.

The server reads this data to display projects and provide the information required by the application.

Using fixture data allows the portal to run without an external database.

### 2.3 Docker

File: `Dockerfile`

The Dockerfile defines the application container.

It specifies the Python runtime, copies the required application files, and configures the server to run inside the container.

### 2.4 Docker Compose

File: `docker-compose.yml`

Docker Compose builds and starts the application container.

The application is exposed on port `8080`.

Run the following command from the project directory:

```bash
docker compose up --build
```

The portal can then be accessed locally at:

`http://localhost:8080`

### 2.5 Acceptance Checker

File: `run.py`

The acceptance checker verifies the required application behavior.

It checks the configured routes, including:

- Public project gallery access
- Project submission rejection for the closed event
- Judge access to scores
- Restrictions on peer-score access
- Participant restrictions on judge scores
- Organizer CSV export

The checker uses the route and authentication configuration in `.dogfood.toml`.

## 3. Request Flow

The portal handles requests in the following order:

1. A browser or acceptance checker sends an HTTP request.
2. Docker forwards the request to the Python server.
3. `server.py` identifies the requested route.
4. The route handler checks access permissions when required.
5. The server reads the necessary information from `fixtures.json`.
6. The server sends an HTTP response to the browser or checker.

### Request Flow Summary

- Browser or Acceptance Checker
- Docker Container
- Python Server (`server.py`)
- Route Handler
- Gallery, Judge Scores, or CSV Export
- Fixture Data (`fixtures.json`)

## 4. Routes

The portal provides the following HTTP routes.

### 4.1 Public Project Gallery

**Route:** `GET /projects`

**Access:** Public

**Purpose:**

- Displays the project gallery.
- Uses fixture data to show sample projects.
- Allows visitors to view the available projects.

### 4.2 Project Submission

**Route:** `POST /projects/new`

**Access:** Participant authentication required

**Purpose:**

- Handles project submission requests.
- Rejects submissions because the event is closed.

### 4.3 Judge Scores

**Route:** `GET /api/judge/scores`

**Access:** Judge authentication required

**Purpose:**

- Allows an authenticated judge to access their own scores.
- Prevents participants from accessing judge scores.

### 4.4 Peer Score Access

**Route:** `GET /api/judge/scores?judge=judge_a`

**Access:** Judge A can access their own scores. Other roles are denied.

**Purpose:**

- Tests access restrictions for peer scores.
- Prevents other judges from accessing Judge A's scores.

### 4.5 Organizer CSV Export

**Route:** `GET /api/export.csv`

**Access:** Organizer authentication required

**Purpose:**

- Allows an authenticated organizer to export judging data.
- Returns the export in CSV format.

## 5. Authentication and Access Control

The portal uses role-based access checks for protected routes.

The configured roles are:

- Organizer
- Judge A
- Judge B
- Participant

The `.dogfood.toml` file contains the authentication configuration used by the acceptance checker.

Protected routes require the appropriate authentication header.

The server checks the authenticated role before allowing access to protected information.

The intended access rules are:

- Public users can access the project gallery.
- Participants cannot access judge scores.
- Judges can access their own scores.
- Judges cannot access another judge's peer scores.
- Organizers can access the CSV export route.

## 6. Data Storage

The application uses local fixture data stored in `fixtures.json`.

This approach keeps the project self-contained and avoids requiring an external database.

The application does not depend on a cloud database or external API.

## 7. Offline Operation

The application is designed to run locally.

Docker Compose starts the application using the files included in the repository.

The application does not require external API calls during normal operation.

The project uses local fixture data and Python's standard library to support the required portal behavior.

## 8. Acceptance Testing

The acceptance checker is configured through `.dogfood.toml`.

Run the following command to generate the acceptance report:

```bash
python3 run.py .dogfood.toml > acceptance-report.txt
```

The generated report records the results of the configured acceptance checks.

The report should be committed to the repository after running the checker.

## 9. Repository Structure

The main project files are:

- `server.py` — Python HTTP server and route handling
- `fixtures.json` — Sample project data
- `Dockerfile` — Container build configuration
- `docker-compose.yml` — Local application startup configuration
- `.dogfood.toml` — Acceptance checker configuration
- `run.py` — Acceptance checker
- `acceptance-report.txt` — Acceptance test results
- `index.html` — Frontend page
- `style.css` — Frontend styling
- `app.js` — Frontend JavaScript
- `README.md` — Project overview and setup instructions
- `ARCHITECTURE.md` — Architecture documentation
- `DATA-MODEL.md` — Data model documentation
- `JUDGING.md` — Judging and evaluation documentation
- `LICENSE` — Project license

## 10. Design Summary

The project uses a simple local architecture:

- Docker Compose manages application startup.
- The Python server handles HTTP requests.
- Route handlers enforce access restrictions.
- Fixture data provides sample project information.
- The acceptance checker verifies the required behavior.

This design keeps the portal self-contained and suitable for local hackathon evaluation.

