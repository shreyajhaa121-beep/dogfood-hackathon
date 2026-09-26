
# Data Model Documentation

## 1. Overview

The portal uses local fixture data stored in `fixtures.json`.

The fixture data provides sample projects for the project gallery and acceptance testing.

The application is designed to run locally without an external database.

## 2. Project Data

Each project represents a sample hackathon submission.

Project records may include the following information:

- Project ID
- Project title
- Project description
- Team or participant information
- Submission status
- Project category

The exact fields depend on the records stored in `fixtures.json`.

## 3. Fixture Data

File: `fixtures.json`

The fixture file contains the sample project records used by the application.

The Python server reads the fixture data when it needs to display project information.

The acceptance checker also uses fixture-related information to verify the required project gallery behavior.

## 4. Project Gallery

The project gallery is available through:

`GET /projects`

The route displays project information from the local fixture data.

The gallery is publicly accessible and does not require authentication.

## 5. Project Submission

Project submission requests use:

`POST /projects/new`

The route requires participant authentication.

Because the hackathon event is closed, new submissions are rejected.

The submission route does not add new projects to the fixture file.

## 6. Judging Data

The portal includes routes for judge score access.

`GET /api/judge/scores`

This route requires judge authentication.

Judges are intended to access their own scores only.

Requests attempting to access another judge's scores are denied.

Participants are not allowed to access judge scores.

## 7. Organizer Export

The organizer export route is:

`GET /api/export.csv`

The route requires organizer authentication.

It returns judging data in CSV format for authorized organizers.

## 8. Data Access and Security

The portal uses role-based access checks for protected routes.

The intended access rules are:

- Public users can view the project gallery.
- Participants cannot access judge scores.
- Judges can access their own scores.
- Judges cannot access peer scores.
- Organizers can access the CSV export route.

Authentication settings are defined in `.dogfood.toml`.

## 9. Storage Design

The project uses local fixture data rather than a database server.

This design keeps the application self-contained and supports offline evaluation.

The fixture file is included in the repository and is available to the application inside the Docker container.

## 10. Summary

The data model is based on local sample project records and role-restricted judging operations.

The project gallery reads fixture data, submission requests are rejected for the closed event, and protected judging and export routes enforce access restrictions.
