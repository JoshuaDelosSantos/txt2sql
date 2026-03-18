"""
This file will return the SQL statements needed to create the database schema.
"""

import logging
import re

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

from results import SQLResult
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    force=True,
)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a PostgreSQL query generator.

Given a natural language question and the relevant database schema below,
write a valid PostgreSQL query that answers the question.

Schema context:
{schema_context}

Rules:
- Return only the raw SQL query — no markdown, no code fences, no explanation
- Use only the tables and columns present in the schema
- Use standard PostgreSQL syntax
- Return an empty string if the question cannot be answered with the given schema
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{query}"),
    ]
)

# Lazy-initialised: built on first call to generate_sql().
chain = None


def _get_chain():
    global chain
    if chain is None:
        settings.require_llm()
        llm = init_chat_model(settings.chat_model, google_api_key=settings.api_key)
        chain = prompt | llm
    return chain