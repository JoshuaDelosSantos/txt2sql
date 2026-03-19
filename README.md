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

# Endpoits
## Check DB connection
```
check-db/

# Returns
{"status": "ok", "message": "Database connection successful."}

# Raises
HTTPException
```