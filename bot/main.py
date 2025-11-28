import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
import telegram_client 
from typing import Optional
from pyrogram import Client


from database import create_db_and_tables
from api import router 

# Load environment variables from .env file
load_dotenv()

# --- CONFIG & SETUP ---

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment variable retrieval with safe defaults
try:
    API_ID = int(os.getenv('API_ID'))
    API_HASH = os.getenv('API_HASH')
#    BOT_TOKEN = os.getenv('BOT_TOKEN')
except (TypeError, ValueError):
    logger.error("FATAL: API_ID, API_HASH, or BOT_TOKEN is missing or invalid in the .env file.")
    # Raise exception to halt execution if critical credentials are missing
    raise

# --- TEMPORARY CHECK ---
print("--- ENV CHECK START ---")
print(f"API_ID: {API_ID}")
print(f"API_HASH: {API_HASH[:4]}...{API_HASH[-4:]}") # Print only start/end for security
#print(f"BOT_TOKEN: {BOT_TOKEN[:4]}...{BOT_TOKEN[-4:]}") # Print only start/end for security
print("--- ENV CHECK END ---")
# --- REMOVE THESE LINES AFTER TESTING ---

# --- LIFECYCLE HANDLER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup (database init, Pyrogram start) and shutdown (Pyrogram stop) events.
    """
    # NOTE: The pyrogram_client variable is managed in telegram_client.py
    
    # 1. Startup tasks
    logger.info("Initializing Database and Tables...")
    create_db_and_tables()
    
    # Create the client instance and assign it to the module-level variable
    telegram_client.pyrogram_client = Client(
        "telegram_scraper_session",
        api_id=API_ID,
        api_hash=API_HASH,
  #      bot_token=BOT_TOKEN if BOT_TOKEN else None,
        in_memory=True
    )


    
    logger.info("Starting Pyrogram Client...")
    try:
        # Pyrogram client MUST be started before any service logic is called
        await telegram_client.pyrogram_client.start()
        logger.info("Pyrogram Client started successfully.")
    except Exception as e:
        # We stop and unassign the client if startup fails
        if telegram_client.pyrogram_client:
             await telegram_client.pyrogram_client.stop()
        telegram_client.pyrogram_client = None
        
        logger.error(f"Failed to start Pyrogram Client. Check API_ID/API_HASH/BOT_TOKEN: {e}")
        # Re-raise to prevent the server from starting with a broken client
        raise
    
    # Yield control back to FastAPI to start accepting requests
    yield
    
    # 2. Shutdown tasks run after the server shuts down
    logger.info("Stopping Pyrogram Client...")
    if telegram_client.pyrogram_client:
        try:
            await telegram_client.pyrogram_client.stop()
        except Exception as e:
            logger.warning(f"Error while stopping Pyrogram client: {e}")
        # Ensure it's explicitly set to None on shutdown
        telegram_client.pyrogram_client = None 

# --- APP ---
app = FastAPI(title="Telegram Scraper Service", version="3.0.0", lifespan=lifespan)

# Register API Routes from api.py
app.include_router(router)

if __name__ == "__main__":
    # Import uvicorn only if running this file directly
    import uvicorn
    logger.info("Starting Uvicorn Server on http://0.0.0.0:8000")
    # This command keeps the server running until manually stopped
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", reload=False, workers=1)