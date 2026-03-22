# Overview
API based Python project that turns natural language into SQL queries.

# Quick Start

## Clone the Repository
```
git clone https://github.com/JoshuaDelosSantos/txt2sql.git
cd txt2sql
```

## Environment Setup
Create a `.env` file in the project root with your database configuration:
```
DB_HOST=your_postgres_host
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
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