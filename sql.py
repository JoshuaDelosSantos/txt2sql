"""
This file will return the SQL statements needed to create the database schema.
"""

import logging
import re
import json
from pathlib import Path

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
- Return only the raw SQL query — no markdown, no code fences, no explanation.
- Use only the tables and columns present in the schema.
- Use standard PostgreSQL syntax.
- Return an empty string if the question cannot be answered with the given schema.
- Label column names with the end user in mind, not the database. For example, if the schema has a column named "cust_id" that refers to customers, label it as "customer_id" in the SQL query for clarity.
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

# Function to load schema for context
def load_schema_context(entity_names: list[str]) -> str:
    """Load and merge schema JSONs for the given entity/table names.

    Returns a formatted string suitable for injection into an LLM prompt.
    """
    schema_dir: Path = settings.schema_dir
    schemas = []

    for name in entity_names:
        logger.info("Loading schema for entity/table: %s", name)
        filepath = schema_dir / f"{name}.json"
        if filepath.exists():
            logger.info("Found schema file: %s", filepath)
            schemas.append(json.loads(filepath.read_text()))
            logger.info("Loaded schema for %s: %s", name, schemas[-1])
        else:
            logger.warning("Schema file not found for %s: %s", name, filepath)

    return json.dumps(schemas, indent=2)

def _strip_fences(text: str) -> str:
    """Remove markdown code fences if the LLM wrapped the output in them."""
    text = text.strip()
    text = re.sub(r"^```(?:sql)?\s*\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n?```$", "", text)
    return text.strip()


def generate_sql(query: str, entities: list[str]) -> str:
    """Return a PostgreSQL query that answers the natural language query.

    Loads schema context from the router for the given entity list, then
    calls the LLM to generate a grounded PostgreSQL query.
    """
    logger.debug("query=%r  entities=%s", query, entities)

    schema_context = load_schema_context(entities)
    response = _get_chain().invoke({"query": query, "schema_context": schema_context})

    usage = getattr(response, "usage_metadata", None)
    if usage:
        logger.info(
            "tokens: %d in / %d out / %d total",
            usage["input_tokens"],
            usage["output_tokens"],
            usage["total_tokens"],
            extra={"token_usage": usage},
        )

    sql = _strip_fences(response.content)

    return SQLResult(sql, usage)

if __name__ == "__main__":
    import entity_extractor as ee
    
    available_tables = ee.get_available_tables()
    query = "How many orders were placed in January?"
    entities = ee.extract_entities(query, available_tables)

    sql = generate_sql(query, entities)
    print(sql)