"""
Functions that can be used to extract the database schema, such as table names, column names, and data types. 
This can be used to help generate SQL queries based on natural language input.
"""

import json
import logging

from config import settings
from db import get_connection

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def _get_tables(cur) -> list[str]:
    cur.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """
    )
    return [row[0] for row in cur.fetchall()]


def _get_columns(cur, table: str) -> list[dict]:
    cur.execute(
        """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position
        """,
        (table,),
    )
    return [
        {
            "name": row[0],
            "type": row[1],
            "nullable": row[2] == "YES",
            "default": row[3],
        }
        for row in cur.fetchall()
    ]


def _get_primary_keys(cur, table: str) -> list[str]:
    cur.execute(
        """
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
           AND tc.table_schema    = kcu.table_schema
        WHERE tc.table_schema   = 'public'
          AND tc.table_name     = %s
          AND tc.constraint_type = 'PRIMARY KEY'
        ORDER BY kcu.ordinal_position
        """,
        (table,),
    )
    return [row[0] for row in cur.fetchall()]


def _get_foreign_keys(cur, table: str) -> list[dict]:
    cur.execute(
        """
        SELECT kcu.column_name,
               ccu.table_name  AS references_table,
               ccu.column_name AS references_column
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
           AND tc.table_schema    = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
            ON tc.constraint_name = ccu.constraint_name
           AND tc.table_schema    = ccu.table_schema
        WHERE tc.table_schema    = 'public'
          AND tc.table_name      = %s
          AND tc.constraint_type = 'FOREIGN KEY'
        """,
        (table,),
    )
    return [
        {
            "column": row[0],
            "references_table": row[1],
            "references_column": row[2],
        }
        for row in cur.fetchall()
    ]


def refresh_schemas() -> list[str]:
    """Introspect the database and write one JSON file per table to schemas/.

    Returns the list of table names written.
    """
    schema_dir = settings.schema_dir
    schema_dir.mkdir(parents=True, exist_ok=True)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            tables = _get_tables(cur)
            logger.info("Found %d tables", len(tables))
            for table in tables:
                schema = {
                    "table": table,
                    "columns": _get_columns(cur, table),
                    "primary_keys": _get_primary_keys(cur, table),
                    "foreign_keys": _get_foreign_keys(cur, table),
                }
                out = schema_dir / f"{table}.json"
                out.write_text(json.dumps(schema, indent=2, default=str))
                logger.info("Wrote schema for table: %s", table)

            (schema_dir / "tables.json").write_text(json.dumps(tables, indent=2))
    finally:
        conn.close()

    return tables

if __name__ == "__main__":
    tables = refresh_schemas()
    logger.info("Refreshed schemas for tables: %s", tables)