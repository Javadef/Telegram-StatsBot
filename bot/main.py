from datetime import date
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session
from typing import List
from database import get_session
from models import ScrapeRequest, ScrapeStatusResponse, Channel, AnalyticsResponse
from repository import TelegramRepository
from service import TelegramService, SCRAPE_STATUS

router = APIRouter()

# Dependency to get Service (needs Pyrogram client from main, so we defer creation or use singleton)
# To handle the dependency cleanly, we'll accept the service instance in the route if possible, 
# or instantiate it using the global client.
def get_repository(session: Session = Depends(get_session)):
    return TelegramRepository(session)

# We will inject the TelegramService from main.py
def get_telegram_service():
    from main import pyrogram_client 
    return TelegramService(pyrogram_client)

@router.post("/api/scrape_channel", response_model=ScrapeStatusResponse)
async def start_scrape(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    service: TelegramService = Depends(get_telegram_service)
):
    """
    Start a scraping task in the background.
    """
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