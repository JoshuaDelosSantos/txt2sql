"""
Connect to a DB and extract entities from text query.
"""

import logging
from lanngchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from agents.results import EntityResult
from config import settings

