"""
API endpoints for the SQL query generator.
"""

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from entity_extractor import extract_entities, get_available_tables
from schema import refresh_schemas
from sql import generate_sql as sql_generate
from db import get_connection

app = FastAPI(title="text2sql", description="Natural language to PostgreSQL")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Models

class QueryRequest(BaseModel):
    quuery: str
    

class TokenUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    

class RequestTokenUsage(BaseModel):
    entity_extraction: TokenUsage | None = None
    sql_generation: TokenUsage | None = None
    total: TokenUsage
    

class GenerateSQLResponse(BaseModel):
    query: str
    entities: list[str]
    sql: str
    token_usage: RequestTokenUsage
    

class ExtractEntitiesResponse(BaseModel):
    query: str
    entities: list[str]
    token_usage: RequestTokenUsage
    

class RefreshSchemasResponse(BaseModel):
    tables: list[str]
    
    
class HealthResponse(BaseModel):
    status: str
    tables: list[str]
    

# Helper functions

def _to_token_usage(usage_dict: dict | None) -> TokenUsage | None:
    if usage_dict is None:
        return None
    return TokenUsage(
        input_tokens=usage_dict["input_tokens"],
        output_tokens=usage_dict["output_tokens"],
        total_tokens=usage_dict["total_tokens"],
    )

def _sum_usage(*usages: TokenUsage | None) -> TokenUsage:
    inp = sum(usage.input_tokens for usage in usages if usage)
    out = sum(usage.output_tokens for usage in usages if usage)
    return TokenUsage(input_tokens=inp, output_tokens=out, total_tokens=inp + out)


# Routes

@app.get("/")
def ui():
    return FileResponse("static/index.html")

@app.get("/check-db")
def check_db():
    try:
        conn = get_connection()
        conn.close()
        return {"status": "ok", "message": "Database connection successful."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")