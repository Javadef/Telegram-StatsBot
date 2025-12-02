import logging
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session
from typing import List, Optional
from database import get_session
from models import ScrapeRequest, ScrapeStatusResponse, Channel, AnalyticsResponse, Message
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

@router.get("/api/scrape_status/{channel_identifier}", response_model=ScrapeStatusResponse)
async def get_scrape_status_by_id(channel_identifier: str):
    """
    Returns the live status of a single, specific scraping task.
    """
    data = SCRAPE_STATUS.get(channel_identifier)
    
    if data is None:
        raise HTTPException(
            status_code=404, 
            detail=f"No active or tracked scrape task found for channel: {channel_identifier}"
        )
        
    return {
        "channel_identifier": channel_identifier,
        "status": data.get("status"),
        "messages_processed": data.get("messages_processed", 0),
        "current_message_date": data.get("current_message_date"),
        "error": data.get("error")
    }

@router.get("/api/channels", response_model=List[Channel])
def list_channels(repo: TelegramRepository = Depends(get_repository)):
    return repo.get_all_channels()

@router.get("/api/channels/{channel_id}", response_model=Optional[Channel])
def get_channel_details(channel_id: int, repo: TelegramRepository = Depends(get_repository)):
    """
    Returns details for a single channel by its internal primary key ID.
    """
    channel = repo.get_channel_by_id(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel

@router.get("/api/analytics", response_model=AnalyticsResponse)
def get_analytics(
    channel_id: int,
    start_date: date,
    end_date: date,
    repo: TelegramRepository = Depends(get_repository)
):
    # Fetch analytics data from repository
    analytics = repo.get_analytics(channel_id, start_date, end_date)
    
    if not analytics or not analytics.get("daily_breakdown"):
        raise HTTPException(status_code=404, detail="No analytics data found for this period")
    
    # Map repo result to AnalyticsResponse
    return AnalyticsResponse(
        channel_id=analytics["channel_id"],
        period_start=analytics["period_start"],
        period_end=analytics["period_end"],
        total_posts=analytics["total_posts"],
        total_views=analytics["total_views"],
        total_reactions=analytics.get("total_reactions", 0),
        total_replies=analytics.get("total_replies", 0),
        total_forwards=analytics.get("total_forwards", 0),
        daily_breakdown=analytics["daily_breakdown"]
    )

@router.get("/api/messages/{channel_id}", response_model=List[Message])
def get_channel_messages(
    channel_id: int, 
    limit: int = 100, 
    offset: int = 0, 
    repo: TelegramRepository = Depends(get_repository)
):
    """
    Get raw messages for a specific channel.
    Uses pagination (limit/offset) to prevent server overload.
    To get all, you can loop through pages or set a high limit.
    """
    # Note: channel_id here should be the Telegram ID (e.g., -100...) 
    # If you meant the internal DB ID, you might need to look up the channel first.
    # Assuming Telegram ID for consistency with other endpoints:
    messages = repo.get_messages_by_channel(channel_id, limit, offset)
    
    if not messages and offset == 0:
         # Optional: Only raise 404 if it's the first page and empty
         # otherwise an empty list is a valid response for "end of pagination"
         raise HTTPException(status_code=404, detail="No messages found for this channel.")
         
    return messages