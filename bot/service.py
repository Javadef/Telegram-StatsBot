import asyncio
import logging
from datetime import date
from typing import Dict
from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.enums import ChatType

from models import ChannelData, MessageData, DailyMetrics
from database import get_session
from repository import TelegramRepository

logger = logging.getLogger(__name__)

# --- SHARED LIVE SCRAPE STATE ---
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

        # --- FETCH CHAT ---
        try:
            chat = await self.client.get_chat(channel_identifier)
        except Exception as e:
            raise Exception(f"Telegram error: {e}")

        if chat.type not in [ChatType.CHANNEL, ChatType.SUPERGROUP]:
            raise Exception("Target is not a channel or supergroup")

        channel_id = chat.id

        # --- UPSERT CHANNEL META ---
        channel_data: ChannelData = {
            "channel_id": channel_id,
            "title": chat.title,
            "username": chat.username,
            "description": chat.description,
            "photo_file_id": chat.photo.big_file_id if chat.photo else None,
            "subscriber_count": getattr(chat, "members_count", None),
            "type": chat.type.name,
            "linked_chat_id": getattr(chat.linked_chat, "id", None)
        }

        repo.upsert_channel(channel_data)

        last_id = repo.get_last_scraped_id(channel_id)
        highest_id_seen = last_id or 0

        self._update_status(channel_identifier, status="running", messages_processed=0)

        messages_buffer = []
        stats_buffer: Dict[date, DailyMetrics] = {}
        processed_count = 0
        BATCH_SIZE = 50

        async for message in self.client.get_chat_history(channel_id):
            try:
                if not message.date:
                    continue

                msg_date = message.date.date()

                # --- DATE BOUNDARY CONTROL ---
                if msg_date > end_date:
                    continue

                if msg_date < start_date:
                    break

                # --- TRACK NEWEST MESSAGE FOR BOOKMARKING ONLY ---
                if message.id > highest_id_seen:
                    highest_id_seen = message.id

                # --- METRICS ---
                views = message.views or 0
                forwards = message.forwards or 0

                reactions = 0
                if message.reactions and message.reactions.reactions:
                    reactions = sum(r.count for r in message.reactions.reactions)

                replies = 0
                try:
                    replies = await self.client.get_discussion_replies_count(
                        chat_id=channel_id,
                        message_id=message.id
                    )
                except Exception:
                    replies_obj = getattr(message, "replies", None)
                    replies = getattr(replies_obj, "total_count", 0)

                # --- BUFFER MESSAGE ---
                message_data: MessageData = {
                    "channel_id": channel_id,
                    "message_id": message.id,
                    "date": message.date,
                    "views": views,
                    "reactions": reactions,
                    "replies": replies,
                    "forwards": forwards
                }

                messages_buffer.append(message_data)

                # --- DAILY STATS BUFFER ---
                if msg_date not in stats_buffer:
                    stats_buffer[msg_date] = DailyMetrics(
                        posts=0,
                        views=0,
                        reactions=0,
                        replies=0,
                        forwards=0
                    )

                stats = stats_buffer[msg_date]
                stats["posts"] += 1
                stats["views"] += views
                stats["reactions"] += reactions
                stats["replies"] += replies
                stats["forwards"] += forwards

                processed_count += 1
                if processed_count % 10 == 0:
                    self._update_status(
                        channel_identifier,
                        messages_processed=processed_count,
                        current_message_date=message.date
                    )

                # --- FLUSH DB BATCH ---
                if len(messages_buffer) >= BATCH_SIZE:
                    repo.upsert_messages(messages_buffer)
                    repo.update_scrape_run(channel_id, highest_id_seen)
                    messages_buffer.clear()

            except FloodWait as e:
                logger.warning(f"FloodWait: sleeping {e.value}s")
                self._update_status(channel_identifier, status=f"paused ({e.value}s)")
                await asyncio.sleep(e.value)
                self._update_status(channel_identifier, status="running")

            except Exception:
                logger.exception(f"Error processing message {message.id}")

        # --- FINAL FLUSH ---
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
