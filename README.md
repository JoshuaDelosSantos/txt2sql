# Overview
Api based Python project that turns natural language into SQL queries

# Quick start
1. Clone repo

2. Build docker image
```
# docker build -t txt2sql .
```

3. Run container. Yourport:containerport
```
# docker run -p 5000:5000 txt2sql
```

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