import asyncio
import logging
from datetime import date
from typing import Dict
from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError
from pyrogram.enums import ChatType
from pyrogram.raw.functions.messages import GetMessageReactionsList
from pyrogram.raw.functions.stats import GetMessagePublicForwards
from pyrogram.raw.types import InputPeerChannel, InputChannel

from database import get_session
from repository import TelegramRepository

logger = logging.getLogger(__name__)

# --- IN-MEMORY SHARED STATE FOR LIVE MONITORING ---
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

        # --- Get chat info ---
        try:
            chat = await self.client.get_chat(channel_identifier)
        except Exception as e:
            raise Exception(f"Telegram Error: {e}")

        if chat.type not in [ChatType.CHANNEL, ChatType.SUPERGROUP]:
            raise Exception("Target is not a channel or supergroup")

        description = chat.description
        photo_file_id = chat.photo.big_file_id if chat.photo else None
        subscriber_count = getattr(chat, "members_count", None)
        chat_type = chat.type.name
        linked_chat_id = getattr(chat.linked_chat, "id", None)
        channel_id = chat.id

        repo.upsert_channel(
            channel_id, chat.title, chat.username,
            description=description,
            photo_file_id=photo_file_id,
            subscriber_count=subscriber_count,
            type=chat_type,
            linked_chat_id=linked_chat_id
        )

        last_id = repo.get_last_scraped_id(channel_id)
        self._update_status(channel_identifier, status="running", messages_processed=0)

        messages_buffer = []
        stats_buffer = {}
        processed_count = 0
        highest_id_seen = last_id if last_id else 0
        BATCH_SIZE = 50

        async for message in self.client.get_chat_history(channel_id):
            try:
                if not message.date:
                    continue

                msg_date = message.date.date()
                if msg_date > end_date:
                    continue
                if msg_date < start_date:
                    break
                if last_id and message.id <= last_id:
                    break

                if message.id > highest_id_seen:
                    highest_id_seen = message.id

                views = message.views or 0

                # --- Reactions (paginated for accuracy) ---
                reactions = 0
                offset_rate = 0
                while True:
                    try:
                        resp = await self.client.invoke(
                            GetMessageReactionsList(
                                peer=InputPeerChannel(channel_id, chat.access_hash),
                                id=message.id,
                                limit=100,
                                offset_rate=offset_rate
                            )
                        )
                        if not getattr(resp, "reactions", None):
                            break
                        reactions += sum(r.count for r in resp.reactions)
                        offset_rate = getattr(resp.reactions[-1], "rate", 0)
                        if len(resp.reactions) < 100:
                            break
                    except Exception:
                        break

                # --- Replies ---
                replies = getattr(message.replies, "total", 0) or 0

                # --- Public forwards (paginated for accuracy) ---
                forwards = 0
                offset_id = 0
                while True:
                    try:
                        resp = await self.client.invoke(
                            GetMessagePublicForwards(
                                channel=InputChannel(channel_id, chat.access_hash),
                                msg_id=message.id,
                                limit=100,
                                offset_id=offset_id,
                                offset_rate=0,
                                offset_peer=None
                            )
                        )
                        forwards += len(getattr(resp, "forwards", []))
                        if len(getattr(resp, "forwards", [])) < 100:
                            break
                        offset_id += len(resp.forwards)
                    except Exception:
                        forwards = 1 if message.forward_from or message.forward_from_chat else 0
                        break

                # --- Buffer message ---
                messages_buffer.append({
                    "channel_id": channel_id,
                    "message_id": message.id,
                    "date": message.date,
                    "views": views,
                    "reactions": reactions,
                    "replies": replies,
                    "forwards": forwards
                })

                # --- Daily stats ---
                if msg_date not in stats_buffer:
                    stats_buffer[msg_date] = {'posts': 0, 'views': 0, 'reactions': 0, 'replies': 0, 'forwards': 0}

                stats_buffer[msg_date]['posts'] += 1
                stats_buffer[msg_date]['views'] += views
                stats_buffer[msg_date]['reactions'] += reactions
                stats_buffer[msg_date]['replies'] += replies
                stats_buffer[msg_date]['forwards'] += forwards

                processed_count += 1
                if processed_count % 10 == 0:
                    self._update_status(
                        channel_identifier,
                        messages_processed=processed_count,
                        current_message_date=message.date
                    )

                # --- Commit batches ---
                if len(messages_buffer) >= BATCH_SIZE:
                    repo.upsert_messages(messages_buffer)
                    repo.update_daily_stats(channel_id, stats_buffer)
                    repo.update_scrape_run(channel_id, highest_id_seen)
                    messages_buffer.clear()
                    stats_buffer.clear()

            except FloodWait as e:
                logger.warning(f"FloodWait detected: sleeping {e.value}s")
                self._update_status(channel_identifier, status=f"paused (floodwait {e.value}s)")
                await asyncio.sleep(e.value)
                self._update_status(channel_identifier, status="running")
            except Exception:
                logger.exception(f"Error processing message {message.id}")

        # --- Final commit ---
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
