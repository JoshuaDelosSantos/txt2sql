const checkButton = document.getElementById("check-db-btn");
const statusEl = document.getElementById("status");
const entityForm = document.getElementById("entity-form");
const queryInput = document.getElementById("query-input");
const entityDisplay = document.getElementById("entity-display");
const generateSqlBtn = document.getElementById("generate-sql-btn");
const sqlDisplay = document.getElementById("sql-display");
const sqlResult = document.getElementById("sql-result");
const tokenLogsContainer = document.getElementById("token-logs");
const tokenDisplay = document.getElementById("token-display");
const executeForm = document.getElementById("execute-form");
const sqlInput = document.getElementById("sql-input");
const executeBtn = document.getElementById("execute-btn");
const resultsDisplay = document.getElementById("results-display");
const resultsContainer = document.getElementById("results-container");
const refreshSchemaBtn = document.getElementById("refresh-schema-btn");
const refreshedTablesEl = document.getElementById("refreshed-tables");
const tablesListEl = document.getElementById("tables-list");

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

function renderTokenUsage(tokenUsage) {
	if (!tokenUsage || !tokenDisplay) {
		return;
	}

	tokenDisplay.innerHTML = '';
	
	const createRow = (label, usage) => {
		const row = document.createElement('div');
		row.style.padding = '5px 0';
		row.style.fontSize = '14px';
		
		if (!usage) {
			row.textContent = `${label}: N/A`;
		} else {
			const inputs = usage.input_tokens || 0;
			const outputs = usage.output_tokens || 0;
			const total = usage.total_tokens || 0;
			row.innerHTML = `<strong>${label}:</strong> Input: ${inputs}, Output: ${outputs}, Total: ${total}`;
		}
		
		return row;
	};

	if (tokenUsage.entity_extraction) {
		tokenDisplay.appendChild(createRow('Entity Extraction', tokenUsage.entity_extraction));
	}

	if (tokenUsage.sql_generation) {
		tokenDisplay.appendChild(createRow('SQL Generation', tokenUsage.sql_generation));
	}

	if (tokenUsage.total) {
		const totalRow = document.createElement('div');
		totalRow.style.padding = '5px 0';
		totalRow.style.fontSize = '14px';
		totalRow.style.fontWeight = 'bold';
		totalRow.style.borderTop = '1px solid #ccc';
		totalRow.style.marginTop = '5px';
		totalRow.style.paddingTop = '5px';
		
		const total = tokenUsage.total;
		const inputs = total.input_tokens || 0;
		const outputs = total.output_tokens || 0;
		const sum = total.total_tokens || 0;
		totalRow.innerHTML = `<strong>Total:</strong> Input: ${inputs}, Output: ${outputs}, Total: ${sum}`;
		tokenDisplay.appendChild(totalRow);
	}

	tokenLogsContainer.style.display = 'block';
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

async function refreshSchema() {
	if (!refreshSchemaBtn || !statusEl) {
		return;
	}

	refreshSchemaBtn.disabled = true;
	statusEl.className = "";
	statusEl.textContent = "Refreshing schema...";

	try {
		const response = await fetch("/refresh-schema", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
		});

		const data = await response.json();

		if (!response.ok) {
			const errorText = data?.detail || "Schema refresh failed.";
			throw new Error(errorText);
		}

		statusEl.className = "ok";
		statusEl.textContent = data?.message || "Schema refreshed successfully.";
		
		// Display the list of refreshed tables
		if (data?.tables && Array.isArray(data.tables)) {
			tablesListEl.innerHTML = '';
			data.tables.forEach(table => {
				const tag = document.createElement('span');
				tag.className = 'entity-tag';
				tag.textContent = table;
				tablesListEl.appendChild(tag);
				tablesListEl.appendChild(document.createTextNode(' '));
			});
			refreshedTablesEl.style.display = 'block';
		}
	} catch (error) {
		statusEl.className = "error";
		statusEl.textContent = error instanceof Error ? error.message : "Unexpected error while refreshing schema.";
		refreshedTablesEl.style.display = 'none';
	} finally {
		refreshSchemaBtn.disabled = false;
	}
}

if (refreshSchemaBtn) {
	refreshSchemaBtn.addEventListener("click", refreshSchema);
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
		renderTokenUsage(data?.token_usage);
	} catch (error) {
		entityDisplay.textContent = error instanceof Error ? error.message : "Unexpected error while checking entities.";
	}
}

if (entityForm) {
	entityForm.addEventListener("submit", checkEntities);
}

async function generateSQL() {
	if (!queryInput || !sqlInput) {
		return;
	}

	const query = queryInput.value.trim();
	if (!query) {
		sqlInput.placeholder = "Please enter a query first.";
		return;
	}

	sqlInput.value = "Generating SQL...";
	sqlInput.disabled = true;

	try {
		const response = await fetch("/generate-sql", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ query }),
		});

		const data = await response.json();

		if (!response.ok) {
			const errorText = data?.detail || "SQL generation failed.";
			throw new Error(errorText);
		}

		const sql = data?.sql || "No SQL generated.";
		sqlInput.value = sql;
		renderTokenUsage(data?.token_usage);
	} catch (error) {
		sqlInput.value = error instanceof Error ? error.message : "Unexpected error while generating SQL.";
	} finally {
		sqlInput.disabled = false;
	}
}

if (generateSqlBtn) {
	generateSqlBtn.addEventListener("click", generateSQL);
}

async function executeQuery(event) {
	event.preventDefault();

	if (!sqlInput || !resultsDisplay || !resultsContainer) {
		return;
	}

	const sql = sqlInput.value.trim();
	if (!sql) {
		resultsContainer.innerHTML = '<p style="color: #b91c1c;">Please enter a SQL query first.</p>';
		resultsDisplay.style.display = "block";
		return;
	}

	resultsContainer.innerHTML = '<p style="color: #6b21a8;">Executing query...</p>';
	resultsDisplay.style.display = "block";

	try {
		const response = await fetch("/execute-query", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ query: sql }),
		});

		const data = await response.json();

		if (!response.ok) {
			const errorText = data?.detail || "Query execution failed.";
			throw new Error(errorText);
		}

		if (data.success) {
			let html = `<div class="query-success">Query executed successfully</div>`;
			
			if (data.columns && data.rows) {
				// Display results as table
				html += '<table>';
				html += '<thead><tr>';
				data.columns.forEach(col => {
					html += `<th>${escapeHtml(col)}</th>`;
				});
				html += '</tr></thead>';
				html += '<tbody>';
				data.rows.forEach(row => {
					html += '<tr>';
					row.forEach(cell => {
						html += `<td>${escapeHtml(cell)}</td>`;
					});
					html += '</tr>';
				});
				html += '</tbody>';
				html += '</table>';
				html += `<p style="margin-top: 1rem; color: #666; font-size: 0.85rem;">Rows: ${data.row_count || 0}</p>`;
			} else if (data.message) {
				html += `<p>${escapeHtml(data.message)}</p>`;
			}
			resultsContainer.innerHTML = html;
		} else {
			const errorType = data.error_type || 'Error';
			const errorMsg = data.error || 'Unknown error occurred.';
			resultsContainer.innerHTML = `
				<div class="query-error">
					<span class="error-type">${escapeHtml(errorType)}</span>
					${escapeHtml(errorMsg)}
				</div>
			`;
		}
	} catch (error) {
		const errorMsg = error instanceof Error ? error.message : "Unexpected error while executing query.";
		resultsContainer.innerHTML = `
			<div class="query-error">
				<span class="error-type">Error</span>
				${escapeHtml(errorMsg)}
			</div>
		`;
	}
}

function escapeHtml(text) {
	const map = {
		'&': '&amp;',
		'<': '&lt;',
		'>': '&gt;',
		'"': '&quot;',
		"'": '&#039;'
	};
	return String(text).replace(/[&<>"']/g, m => map[m]);
}

if (executeForm) {
	executeForm.addEventListener("submit", executeQuery);
}
