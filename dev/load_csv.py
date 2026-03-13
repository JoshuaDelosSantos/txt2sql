"""
Load mock csv data into Postgres database.
"""

import os
import sys
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")

