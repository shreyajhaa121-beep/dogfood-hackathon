
# Judging and Evaluation Documentation

## 1. Overview

This document explains how the hackathon portal supports judging-related access and how the application is evaluated.

The portal includes judge score access, peer-score restrictions, and organizer CSV export.

## 2. User Roles

The application uses the following roles:

- **Organizer:** Can access the judging CSV export.
- **Judge A:** Can access their own scores.
- **Judge B:** Can access their own scores but cannot access Judge A's peer scores.
- **Participant:** Cannot access judge scores.

## 3. Judging Routes

### 3.1 Judge Scores

**Route:** `GET /api/judge/scores`

**Access:** Authenticated judges

This route allows an authenticated judge to access their own scores.

### 3.2 Peer Score Restriction

**Route:** `GET /api/judge/scores?judge=judge_a`

Judge A can access their own scores.

Other roles are denied access to Judge A's peer scores. The expected denial response is HTTP `401` or `403`.

### 3.3 Participant Restriction

Participants must not be able to access judge scores.

A participant request to the judge scores route should return HTTP `401` or `403`.

### 3.4 Organizer CSV Export

**Route:** `GET /api/export.csv`

**Access:** Authenticated organizer

The route allows an authorized organizer to export judging data in CSV format.

The expected successful response is HTTP `200` with CSV content.

## 4. Authentication

The acceptance checker uses authentication settings from `.dogfood.toml`.

The configuration defines authentication headers for the organizer, judges, and participant.

Protected routes check the supplied authentication information before allowing access.

## 5. Acceptance Checks

The acceptance checker verifies the following judging-related behaviors:

1. Judge A can access their own scores.
2. Judge B cannot access Judge A's peer scores.
3. A participant cannot access judge scores.
4. An organizer can access the CSV export.
5. The CSV export returns a successful response with CSV content.

The checker records the results in `acceptance-report.txt`.

## 6. Running the Acceptance Checker

Run the following command from the project directory:

```bash
python3 run.py .dogfood.toml > acceptance-report.txt
```

Review the generated report to confirm the results of the configured checks.

If application code or configuration changes, run the checker again and commit the updated report.

## 7. Evaluation Notes

The acceptance checker validates the configured routes and expected HTTP responses.

A passing report indicates that the configured checks passed during that run. It does not independently prove that every possible security scenario has been tested.

## 8. Summary

The portal demonstrates role-based access to judging features.

Judges are restricted to their own scores, participants are blocked from judge score access, and organizers can export judging data through the protected CSV route.
