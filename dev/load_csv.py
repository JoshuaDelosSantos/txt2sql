"""
Load mock csv data into Postgres database.
"""

import os
import sys
from pathlib import Path
import psycopg2
from dotenv import load_dotenv
from db import get_connection

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")

CSV_DIR = ROOT_DIR / "dev" / "csv_data"

def main():
    pass

def drop_all(current):
    pass

def copy_table(current, table_name):
    pass