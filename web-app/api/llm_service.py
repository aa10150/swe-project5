"""
llm_service.py

Module for generating course recommendations using OpenAI GPT-4.
"""

import json
import os
from typing import Dict, List, Optional

from openai import OpenAI


# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY not set in environment variables. "
        "Please set it in your .env file."
    )

client = OpenAI(api_key=OPENAI_API_KEY)

