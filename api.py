"""
API endpoints for the SQL query generator.
"""

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from entity_extractor import extract_entities, get_available_tables
from schema import refresh_schemas
from sql import generate_sql as sql_generate

app = FastAPI(title="text2sql", description="Natural language to PostgreSQL")


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
    
    