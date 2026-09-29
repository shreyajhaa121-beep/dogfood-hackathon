
/*
 * Dogfood Hackathon Portal
 * Frontend API integration
 *
 * Replace this placeholder with your Codespaces
 * forwarded Port 8080 URL, without a trailing slash.
 */
const API_BASE_URL = "https://upgraded-waffle-4q7wgqwx6r6r2qxj-8080.app.github.dev";

function apiUrl(path) {
  return `${API_BASE_URL}${path}`;
}

function setMessage(elementId, message, isError = false) {
  const element = document.getElementById(elementId);
  if (!element) return;

  element.textContent = message;
  element.style.color = isError ? "#b91c1c" : "#166534";
}

function getToken(inputId) {
  return document.getElementById(inputId)?.value.trim() || "";
}

// Load public project gallery
async function loadProjects() {
  const gallery = document.getElementById("project-gallery");
  if (!gallery) return;

  try {
    const response = await fetch("fixtures.json");
    if (!response.ok) throw new Error("Could not load fixtures.json");

    const data = await response.json();
    const projects = data.projects || [];

    gallery.replaceChildren();

    if (projects.length === 0) {
      gallery.textContent = "No projects available.";
      return;
    }

    projects.forEach((project) => {
      const card = document.createElement("article");
      card.className = "project-card";

      const title = document.createElement("h3");
      title.textContent = project.title || "Untitled project";

      const summary = document.createElement("p");
      summary.textContent =
        project.summary ||
        project.description ||
        "No description available.";

      const link = document.createElement("a");
      link.textContent = "View project details";
      link.href =
        "project-details.html?id=" +
        encodeURIComponent(project.id || "");

      card.append(title, summary, link);
      gallery.appendChild(card);
    });
  } catch (error) {
    gallery.textContent =
      "Could not load projects. Please check the fixture file.";
    console.error(error);
  }
}

// Load judge's permitted scores
async function loadJudgeScores() {
  const token = getToken("judge-token");

  if (!token) {
    setMessage("judge-message", "Enter your judge demo token.", true);
    return;
  }

  const button = document.getElementById("load-scores-button");
  const output = document.getElementById("judge-scores");

  button.disabled = true;
  output.replaceChildren();
  setMessage("judge-message", "Loading scores...");

  try {
    const response = await fetch(apiUrl("/api/judge/scores"), {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.error || `Request failed (${response.status})`);
    }

    const scores = Array.isArray(data)
      ? data
      : data.scores || data.results || [];

    if (scores.length === 0) {
      setMessage("judge-message", "No scores available for this judge.");
      return;
    }

    const table = document.createElement("table");
    table.className = "score-table";

    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    ["Project", "Score"].forEach((heading) => {
      const th = document.createElement("th");
      th.textContent = heading;
      headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");

    scores.forEach((item) => {
      const row = document.createElement("tr");

      const projectCell = document.createElement("td");
      projectCell.textContent =
        item.project_title ||
        item.title ||
        item.project_id ||
        "Project";

      const scoreCell = document.createElement("td");
      scoreCell.textContent =
        item.score !== undefined ? String(item.score) : "—";

      row.append(projectCell, scoreCell);
      tbody.appendChild(row);
    });

    table.appendChild(tbody);
    output.appendChild(table);
    setMessage("judge-message", "Scores loaded.");
  } catch (error) {
    setMessage("judge-message", error.message, true);
  } finally {
    button.disabled = false;
  }
}

// Organizer-only CSV export
async function exportScoresCsv() {
  const token = getToken("organizer-token");

  if (!token) {
    setMessage("export-message", "Enter the organizer demo token.", true);
    return;
  }

  const button = document.getElementById("export-csv-button");
  button.disabled = true;
  setMessage("export-message", "Preparing CSV export...");

  try {
    const response = await fetch(apiUrl("/api/export.csv"), {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.error || `Export failed (${response.status})`);
    }

    const csvText = await response.text();
    const blob = new Blob([csvText], {
      type: "text/csv;charset=utf-8;"
    });

    const downloadUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = downloadUrl;
    link.download = "judging-scores.csv";
    document.body.appendChild(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(downloadUrl);
    setMessage("export-message", "CSV download started.");
  } catch (error) {
    setMessage("export-message", error.message, true);
  } finally {
    button.disabled = false;
  }
}

// Display event status
async function loadEventStatus() {
    const statusElement = document.getElementById('event-status');

    try {
        const response = await fetch(apiUrl("/api/event"));
        if (!response.ok) throw new Error("Could not load event status.");

        const data = await response.json();
        const closesAt = data.event?.submissions_close;

        const eventStatus = closesAt
            ? (new Date(closesAt) > new Date() ? "Open" : "Closed")
            : "Unknown";

        statusElement.textContent = `Event status: ${eventStatus}`;
    } catch (error) {
        statusElement.textContent =
            "Event status could not be loaded. Check the backend connection.";
        console.error(error);
    }
}

async function submitProject(event) {
  event.preventDefault();

  const token = getToken("participant-token");

  if (!token) {
    setMessage(
      "submission-message",
      "Enter the participant demo token.",
      true
    );
    return;
  }

  const button = document.getElementById("submit-project-button");
  button.disabled = true;
  setMessage("submission-message", "Checking submission status...");

  try {
    const response = await fetch(apiUrl("/projects/new"), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    const data = await response.json().catch(() => ({}));

    if (response.status === 409) {
      setMessage(
        "submission-message",
        data.error || "Submissions are closed for this event.",
        true
      );
      return;
    }

    if (!response.ok) {
      throw new Error(data.error || `Request failed (${response.status})`);
    }

    setMessage(
      "submission-message",
      data.message || "Submission request received."
    );
  } catch (error) {
    setMessage("submission-message", error.message, true);
  } finally {
    button.disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadProjects();
  loadEventStatus();

  document
    .getElementById("load-scores-button")
    ?.addEventListener("click", loadJudgeScores);

  document
    .getElementById("export-csv-button")
    ?.addEventListener("click", exportScoresCsv);

  document
    .getElementById("submission-form")
    ?.addEventListener("submit", submitProject);
});
