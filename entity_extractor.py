"""
Connect to a DB and extract entities from text query.
"""

import logging
from lanngchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from agents.results import EntityResult
from config import settings

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class EntityList(BaseModel):
    entities: list[str] = Field(..., description="List of entities extracted from the database.")
    

SYSTEM_PROMPT = """\
You are a database entity extractor for a text-to-SQL system.

Given a natural language query and the list of available database tables below,
identify which tables are needed to answer the query.

Available tables:
{tables}

Rules:
- Only return table names from the list above — never invent new names
- Include tables required for JOINs even if not explicitly mentioned in the query
- Return nothing if query is not asking for any data or if it cannot be answered with the available tables    

"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{query}"),
    ]
)