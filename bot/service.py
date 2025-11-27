import asyncio
import logging
from datetime import date, datetime, timedelta
from typing import Dict, Optional, List
from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError
from pyrogram.enums import ChatType
from database import get_session
from repository import TelegramRepository

logger = logging.getLogger(__name__)

# --- IN-MEMORY SHARED STATE FOR LIVE MONITORING ---
# Structure: { "channel_identifier": { "status": "running", "processed": 0, ... } }
SCRAPE_STATUS: Dict[str, Dict] = {}

class TelegramService:
    def __init__(self, client: Client):
        self.client = client

    def _update_status(self, key: str, **kwargs):
        if key not in SCRAPE_STATUS:
            SCRAPE_STATUS[key] = {
                "status": "pending", 
                "messages_processed": 0, 
                "current_message_date": None,
                "error": None
            }
        SCRAPE_STATUS[key].update(kwargs)

    async def scrape_channel_task(self, channel_identifier: str, start_date: date, end_date: date):
        """
        Background task wrapper to handle DB session lifecycle independently.
        """
        # Create a new session for this background task
        session_gen = get_session()
        session = next(session_gen)
        repo = TelegramRepository(session)
        
        try:
            await self._scrape_logic(repo, channel_identifier, start_date, end_date)
        except Exception as e:
            logger.error(f"Background scrape failed for {channel_identifier}: {e}")
            self._update_status(channel_identifier, status="failed", error=str(e))
        finally:
            session.close()

    async def _scrape_logic(self, repo: TelegramRepository, channel_identifier: str, start_date: date, end_date: date):
        self._update_status(channel_identifier, status="initializing")
        
        try:
            chat = await self.client.get_chat(channel_identifier)
        except Exception as e:
            raise Exception(f"Telegram Error: {e}")

        if chat.type not in [ChatType.CHANNEL, ChatType.SUPERGROUP]:
            raise Exception("Target is not a channel or supergroup")

        channel_id = chat.id
        repo.upsert_channel(channel_id, chat.title, chat.username)

        # Checkpoint
        last_id = repo.get_last_scraped_id(channel_id)
        
        self._update_status(channel_identifier, status="running", messages_processed=0)
        
        messages_buffer = []
        stats_buffer = {}
        processed_count = 0
        highest_id_seen = last_id if last_id else 0
        
        # Batch size for DB commits
        BATCH_SIZE = 50 

        # Pyrogram iterates Newest -> Oldest
        async for message in self.client.get_chat_history(channel_id):
            try:
                # 1. Check End Date (Skip future messages if end_date is in past relative to message)
                # If message is NEWER than end_date, we just skip it but keep iterating to find older ones.
                if message.date.date() > end_date:
                    continue

                # 2. Check Start Date (Stop if we went too far back)
                if message.date.date() < start_date:
                    logger.info(f"Reached start date limit {start_date}. Stopping.")
                    break

                # 3. Check Checkpoint (Stop if we reached previously scraped data)
                # NOTE: Only applies if message is strictly older than what we have, 
                # ensuring we don't re-scrape the same ID unless needed.
                if last_id and message.id <= last_id:
                    logger.info(f"Reached last scraped ID {last_id}. Stopping.")
                    break

                # Update tracking
                if message.id > highest_id_seen:
                    highest_id_seen = message.id

                # Process Message
                msg_date = message.date.date()
                views = message.views or 0

                messages_buffer.append({
                    "channel_id": channel_id,
                    "message_id": message.id,
                    "date": message.date,
                    "views": views
                })

                if msg_date not in stats_buffer:
                    stats_buffer[msg_date] = {'posts': 0, 'views': 0}
                stats_buffer[msg_date]['posts'] += 1
                stats_buffer[msg_date]['views'] += views

                processed_count += 1
                
                # Update Live Status every few messages
                if processed_count % 10 == 0:
                    self._update_status(
                        channel_identifier, 
                        messages_processed=processed_count, 
                        current_message_date=message.date
                    )

                # Batch Insert to DB
                if len(messages_buffer) >= BATCH_SIZE:
                    repo.upsert_messages(messages_buffer)
                    repo.update_daily_stats(channel_id, stats_buffer)
                    repo.update_scrape_run(channel_id, highest_id_seen)
                    messages_buffer.clear()
                    stats_buffer.clear()

            except FloodWait as e:
                logger.warning(f"FloodWait detected. Sleeping for {e.value} seconds.")
                self._update_status(channel_identifier, status=f"paused (floodwait {e.value}s)")
                await asyncio.sleep(e.value)
                self._update_status(channel_identifier, status="running")
                continue
            except Exception as e:
                logger.error(f"Error processing message {message.id}: {e}")
                continue

        # Final Commit
        if messages_buffer:
            repo.upsert_messages(messages_buffer)
            repo.update_daily_stats(channel_id, stats_buffer)
        
        repo.update_scrape_run(channel_id, highest_id_seen)
        
        self._update_status(
            channel_identifier, 
            status="completed", 
            messages_processed=processed_count,
            current_message_date=None
        )

    def get_active_tasks(self) -> Dict:
        return SCRAPE_STATUS