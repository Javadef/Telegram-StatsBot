from pyrogram import Client
from typing import Optional

# Initialize as None, to be set by main.py's lifespan event
pyrogram_client: Optional[Client] = None