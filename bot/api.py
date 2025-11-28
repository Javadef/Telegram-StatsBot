import logging
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session
from typing import List, Optional
from database import get_session
from models import ScrapeRequest, ScrapeStatusResponse, Channel, AnalyticsResponse
from repository import TelegramRepository
from service import TelegramService, SCRAPE_STATUS
import telegram_client 

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency to get Repository
def get_repository(session: Session = Depends(get_session)):
    return TelegramRepository(session)

# Dependency to get Service - MUST ENSURE CLIENT IS CONNECTED
def get_telegram_service():
    # Check the variable directly on the imported module
    client_instance = telegram_client.pyrogram_client 
    
    # Check if the client is None 
    if client_instance is None:
        logger.error("Pyrogram client is None. Client initialization failed in main.")
        raise HTTPException(
            status_code=503, 
            detail="Scraper service is unavailable. Telegram client is not initialized."
        )

    # Use is_connected on the retrieved instance
    if not client_instance.is_connected:
        logger.error("Pyrogram client is not connected. Cannot create TelegramService.")
        raise HTTPException(
            status_code=503, 
            detail="Scraper service is unavailable. Telegram client not connected to Telegram servers."
        )
        
    return TelegramService(client_instance)

@router.post("/api/scrape_channel", response_model=ScrapeStatusResponse)
async def start_scrape(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    service: TelegramService = Depends(get_telegram_service) # Client is guaranteed to be connected here
):
    """
    Start a scraping task in the background.
    """
    logger.info(f"Starting background scrape for channel: {request.channel_identifier}")
    
    # Initialize status
    service._update_status(request.channel_identifier, status="pending")
    
    # Default end_date to today if not provided
    end_dt = request.end_date if request.end_date else date.today()
    
    # Add to background tasks
    background_tasks.add_task(
        service.scrape_channel_task,
        request.channel_identifier,
        request.start_date,
        end_dt
    )
    
    return {
        "channel_identifier": request.channel_identifier,
        "status": "pending",
        "messages_processed": 0
    }

@router.get("/api/scrape_status", response_model=List[ScrapeStatusResponse])
async def get_scrape_status():
    """
    Returns the live status of all tracked scraping tasks.
    """
    results = []
    for identifier, data in SCRAPE_STATUS.items():
        results.append({
            "channel_identifier": identifier,
            "status": data.get("status"),
            "messages_processed": data.get("messages_processed", 0),
            "current_message_date": data.get("current_message_date"),
            "error": data.get("error")
        })
    return results

@router.get("/api/channels", response_model=List[Channel])
def list_channels(repo: TelegramRepository = Depends(get_repository)):
    return repo.get_all_channels()

@router.get("/api/analytics", response_model=AnalyticsResponse)
def get_analytics(
    channel_id: int, 
    start_date: date, 
    end_date: date,
    repo: TelegramRepository = Depends(get_repository)
):
    return repo.get_analytics(channel_id, start_date, end_date)