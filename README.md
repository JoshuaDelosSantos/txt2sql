# Overview
API based Python project that turns natural language into SQL queries.

# Quick Start

## Clone the Repository
```
git clone https://github.com/JoshuaDelosSantos/txt2sql.git
cd txt2sql
```

## Environment Setup

### Database Configuration
Create a `.env` file in the project root with your database configuration:
```
DB_HOST=your_postgres_host
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
```

### API Key and LLM Configuration
Currently, we only have support for Gemini models

1. **Get a Google Gemini API Key:**
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Sign in with your Google account
   - Create a new API key
   - Copy the key and add it to your `.env` file

2. **Configure the API Key and Model:**
   ```
   API_KEY=your_google_gemini_api_key
   CHAT_MODEL=google_genai:gemini-2.5-flash-lite
   ```

## Run with Docker Compose
```
docker compose up
```

The application will be available at `http://localhost:5000`

## Database Configuration

### Using the Included PostgreSQL template in compose
The `docker-compose.yml` includes a PostgreSQL image pre-configured with the bike relational database.

Environment variables for the included container:
```
DB_HOST=postgres
DB_PORT=5432
DB_NAME=bikestore
DB_USER=postgres
DB_PASSWORD=postgres
```

### Load Sample Data
To populate the included database with sample data, execute:
```
python -m dev.load_csv
```

This loads CSV files from the `dev/csv/` directory into the database, including:
- Brands
- Categories
- Customers
- Orders
- Products
- Staffs
- Stocks
- Stores

### Using Your Own Database
To connect to an external PostgreSQL database, update the `.env` file with your connection details and ensure the database name, user, and password are correctly configured before running Docker Compose.

# How It Works

## SQL Generation Flow

The application uses a multi-stage process to convert natural language queries into SQL:

1. **Schema Introspection** — Database schema is introspected to extract table structures, column definitions, and relationships. This information is persisted as JSON files in the `schemas/` directory.

2. **Entity Extraction** — The natural language query is analysed by an LLM to identify which database tables are relevant to answering the question.

3. **Schema Context Loading** — The JSON schema files for identified entities are retrieved and merged into a single context document.

4. **SQL Generation** — The natural language query and schema context are sent to the Gemini API, which generates valid PostgreSQL syntax.

5. **Query Execution** — The generated (or user-provided) SQL query is executed against the connected database, returning results or error messages.

# Endpoints

## Check DB Connection
`GET /check-db`

Returns database connection status.

```
# Response
{"status": "ok", "message": "Database connection successful."}
```

## Extract Entities
`POST /extract-entities`

Extracts entities from a natural language query.

Request body:
```
{"query": "your query here"}
```

Response:
```
{
  "query": "your query here",
  "entities": ["entity1", "entity2"],
  "token_usage": {
    "entity_extraction": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
    "total": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
  }
}
```

## Generate SQL
`POST /generate-sql`

Generates SQL from a natural language query, including entity extraction and token tracking.

Request body:
```
{"query": "your query here"}
```

Response:
```
{
  "query": "your query here",
  "entities": ["entity1", "entity2"],
  "sql": "SELECT * FROM table WHERE condition",
  "token_usage": {
    "entity_extraction": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
    "sql_generation": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
    "total": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
  }
}
```

## Execute Query
`POST /execute-query`

Executes a PostgreSQL query against the connected database.

Request body:
```
{"query": "SELECT * FROM table WHERE id = 1"}
```

Response (on success):
```
{
  "success": true,
  "columns": ["id", "name"],
  "rows": [["1", "value"]],
  "row_count": 1
}
```

Response (on error):
```
{
  "success": false,
  "error": "Error message describing the issue",
  "error_type": "SyntaxError"
}
```

## Refresh Schema
`POST /refresh-schema`

Introspects the connected database and refreshes schema definitions. This must be executed after connecting to a new database or after schema changes.

Response:
```
{
  "success": true,
  "tables": ["table1", "table2", "table3"],
  "message": "Schema refreshed successfully. 3 table(s) found."
}
```

# Flow


