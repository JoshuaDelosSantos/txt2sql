const checkButton = document.getElementById("check-db-btn");
const statusEl = document.getElementById("status");
const entityForm = document.getElementById("entity-form");
const queryInput = document.getElementById("query-input");
const entityDisplay = document.getElementById("entity-display");

function renderEntities(entities) {
    const c = document.getElementById('entity-display');
    c.innerHTML = '';
		entities.forEach((e) => {
      const tag = document.createElement('span');
      tag.className = 'entity-tag';
			if (typeof e === "string") {
				tag.textContent = e;
			} else if (e && typeof e === "object") {
				const candidate = e.entity || e.name || e.table || e.value;
				tag.textContent = typeof candidate === "string" ? candidate : JSON.stringify(e);
			} else {
				tag.textContent = String(e);
			}
      c.appendChild(tag);
			c.appendChild(document.createTextNode(' '));
    });
}

async function checkDatabaseConnection() {
	if (!checkButton || !statusEl) {
		return;
	}

	checkButton.disabled = true;
	statusEl.className = "";
	statusEl.textContent = "Checking database connection...";

	try {
		const response = await fetch("/check-db");
		const data = await response.json();

		if (!response.ok) {
			const errorText = data?.detail || "Database connection check failed.";
			throw new Error(errorText);
		}

		statusEl.className = "ok";
		statusEl.textContent = data?.message || "Database connection successful.";
	} catch (error) {
		statusEl.className = "error";
		statusEl.textContent = error instanceof Error ? error.message : "Unexpected error while checking DB connection.";
	} finally {
		checkButton.disabled = false;
	}
}

if (checkButton) {
	checkButton.addEventListener("click", checkDatabaseConnection);
}

async function checkEntities(event) {
	event.preventDefault();

	if (!queryInput || !entityDisplay) {
		return;
	}

	const query = queryInput.value.trim();
	if (!query) {
		entityDisplay.textContent = "Please enter a query first.";
		return;
	}

	entityDisplay.textContent = "Checking entities...";

	try {
		const response = await fetch("/extract-entities", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ query }),
		});

		const data = await response.json();

		if (!response.ok) {
			const errorText = data?.detail || "Entity extraction failed.";
			throw new Error(errorText);
		}

		const entities = Array.isArray(data?.entities) ? data.entities : [];
		if (entities.length === 0) {
			entityDisplay.textContent = "No entities found.";
			return;
		}

		renderEntities(entities);
	} catch (error) {
		entityDisplay.textContent = error instanceof Error ? error.message : "Unexpected error while checking entities.";
	}
}

if (entityForm) {
	entityForm.addEventListener("submit", checkEntities);
}
