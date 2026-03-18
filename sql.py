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