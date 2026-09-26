async function loadProjects() {
  const gallery = document.getElementById("project-gallery");

  try {
    const response = await fetch("fixtures.json");

    if (!response.ok) {
      throw new Error("Could not load fixtures.json");
    }

    const data = await response.json();
    const projects = data.projects || [];

    if (projects.length === 0) {
      gallery.textContent = "No projects available.";
      return;
    }

    gallery.replaceChildren();

    projects.forEach((project) => {
      const card = document.createElement("article");
      card.className = "project-card";

      const title = document.createElement("h3");
      title.textContent = project.title || "Untitled project";

      const summary = document.createElement("p");
      summary.textContent =
        project.summary || project.description || "No description available.";

      card.append(title, summary);
      gallery.appendChild(card);
    });
  } catch (error) {
    gallery.textContent =
      "Could not load projects. Please check the fixture file.";
    console.error(error);
  }
}

document.addEventListener("DOMContentLoaded", loadProjects);
