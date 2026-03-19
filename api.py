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

