"""
Connect to a DB and extract entities from text query.
"""

import logging
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from results import EntityResult
from config import settings
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    force=True,
)
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

chain = None

def _get_chain():
    global chain
    if chain is None:
        settings.require_llm()
        llm = init_chat_model(settings.chat_model, google_api_key=settings.api_key)
        structured_llm = llm.with_structured_output(EntityList, include_raw=True)
        chain = prompt | structured_llm
    return chain

def get_available_tables() -> list[str]:
        """Return table names from the index written by the schema agent."""
        tables_path = settings.schema_dir / "tables.json"
        logger.info("Looking for available tables in %s", tables_path)
        if not tables_path.exists():
            logger.info("Tables file not found.")
            return []
        logger.info("Found tables file.")

        return json.loads(tables_path.read_text())

def extract_entities(query: str, available_tables: list[str]) -> list[str]:
    """Return the subset of available_tables relevant to the user query.

    Calls the LLM to identify relevant tables, then filters the result to
    only names present in available_tables as a guard against hallucination.
    """
    tables_str = "\n".join(f"- {t}" for t in available_tables)

    logger.info("query=%r  available=%s", query, available_tables)

    result = _get_chain().invoke({"query": query, "tables": tables_str})
    raw = result["raw"]
    parsed: EntityList = result["parsed"]

    logger.info("llm returned: %s", parsed.entities)

    usage = getattr(raw, "usage_metadata", None)
    if usage:
        logger.info(
            "tokens: %d in / %d out / %d total",
            usage["input_tokens"],
            usage["output_tokens"],
            usage["total_tokens"],
            extra={"token_usage": usage},
        )

    entities = [t for t in parsed.entities if t in available_tables]
    logger.info("filtered: %s", entities)

    return EntityResult(entities, usage)

if __name__ == "__main__":
    available_tables = get_available_tables()
    query = "How many orders were placed in January?"
    entities = extract_entities(query, available_tables)
    print(entities)