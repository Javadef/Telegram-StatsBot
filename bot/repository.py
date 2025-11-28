from typing import List, Optional, Dict
from datetime import date, datetime
from sqlmodel import Session, select, col, and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func
from models import Channel, Message, ChannelStatsDaily, ScrapeRun
from models import ChannelData, MessageData, DailyMetrics 

class TelegramRepository:
    def __init__(self, session: Session):
        self.session = session # Session is passed in, management (commit/rollback) is done externally or explicitly

    # --- SESSION HANDLING IMPROVEMENT (Conceptual) ---
    # The ideal usage would be:
    # with get_session() as session:
    #     repo = TelegramRepository(session)
    #     repo.upsert_channel(...)
    # For now, we keep commit/refresh inside the methods, but note the self.session management below.

    # 1. OPTIONAL FIELDS IN UPSERTS
    # ⚠️ FIX: Updated to accept and update all relevant Channel fields.
    # ⚠️ FIX: Change the signature to accept the ChannelData TypedDict
    def upsert_channel(self, channel_data: ChannelData) -> Channel:
        # Use a context manager for safe session handling
        with self.session:
            channel = self.session.exec(
                select(Channel).where(Channel.channel_id == channel_data['channel_id'])
            ).first()
            
            # --- The logic to handle all fields is already correct here ---
            if channel:
                # Update all fields provided in channel_data
                for key, value in channel_data.items():
                    if key != 'channel_id':
                        # The key name matches the model field name
                        setattr(channel, key, value) 
                self.session.add(channel)
            else:
                # Unpack the dictionary to create a new Channel object
                channel = Channel(**channel_data) 
                self.session.add(channel)
                
            self.session.commit()
            self.session.refresh(channel)
            return channel

    # 2. BULK UPSERT PERFORMANCE
    # ⚠️ FIX: Implemented bulk ON CONFLICT DO UPDATE using the PostgreSQL dialect's insert function.
    def upsert_messages(self, messages_data: List[MessageData]):
        if not messages_data:
            return

        # Convert list of TypedDicts to list of dicts for SQLAlchemy
        data_to_insert = [dict(msg) for msg in messages_data]

        # Use the PostgreSQL bulk insert/upsert capability
        # NOTE: This requires PostgreSQL. For SQLite/MySQL, you'd need different strategies.
        stmt = insert(Message).values(data_to_insert)

        # Specify which fields to update on conflict
        # The index_elements are the primary/unique key(s) that define the conflict: ('channel_id', 'message_id')
        update_cols = {
            "views": stmt.excluded.views,
            "reactions": stmt.excluded.reactions,
            "replies": stmt.excluded.replies,
            "forwards": stmt.excluded.forwards,
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=["channel_id", "message_id"],
            set_=update_cols
        )
        
        # Execute and commit in a single transaction
        with self.session:
            self.session.execute(stmt)
            self.session.commit()

    # 3. UPDATE DAILY STATS EXTENSIBILITY
    # ⚠️ FIX: Updated to handle new reaction/reply/forward metrics.
    def update_daily_stats(self, channel_id: int, stats_buffer: Dict[date, DailyMetrics]):
        with self.session:
            for date_key, metrics in stats_buffer.items():
                stats = self.session.exec(
                    select(ChannelStatsDaily).where(
                        ChannelStatsDaily.channel_id == channel_id, 
                        ChannelStatsDaily.message_date == date_key
                    )
                ).first()

                if stats:
                    stats.post_count += metrics['posts']
                    stats.total_views += metrics['views']
                    stats.total_reactions += metrics.get('reactions', 0) # Use .get for robustness
                    stats.total_replies += metrics.get('replies', 0)     # Use .get for robustness
                    stats.total_forwards += metrics.get('forwards', 0)   # Use .get for robustness
                else:
                    stats = ChannelStatsDaily(
                        channel_id=channel_id, 
                        message_date=date_key,
                        post_count=metrics['posts'], 
                        total_views=metrics['views'],
                        total_reactions=metrics.get('reactions', 0),
                        total_replies=metrics.get('replies', 0),
                        total_forwards=metrics.get('forwards', 0),
                    )
                self.session.add(stats)
            
            # Commit all changes for the loop at once (bulk transaction)
            self.session.commit()

    def get_channel_by_id(self, pk_id: int) -> Optional[Channel]:
         return self.session.get(Channel, pk_id)
    
    def get_last_scraped_id(self, channel_id: int) -> Optional[int]:
        run = self.session.exec(select(ScrapeRun).where(ScrapeRun.channel_id == channel_id)).first()
        return run.last_scraped_id if run else None

    def update_scrape_run(self, channel_id: int, last_id: int):
        run = self.session.exec(select(ScrapeRun).where(ScrapeRun.channel_id == channel_id)).first()
        if run:
            if last_id > (run.last_scraped_id or 0):
                run.last_scraped_id = last_id
            run.last_scraped_at = datetime.utcnow()
            self.session.add(run)
        else:
            run = ScrapeRun(channel_id=channel_id, last_scraped_id=last_id, last_scraped_at=datetime.utcnow())
            self.session.add(run)
        self.session.commit()

    def get_all_channels(self) -> List[Channel]:
        return self.session.exec(select(Channel)).all()

    # 4. Analytics Update (Minimal for now)
    def get_analytics(self, channel_id: int, start_date: date, end_date: date) -> Dict:
        query = select(ChannelStatsDaily).where(
            ChannelStatsDaily.channel_id == channel_id,
            ChannelStatsDaily.message_date >= start_date,
            ChannelStatsDaily.message_date <= end_date
        ).order_by(ChannelStatsDaily.message_date)

        results = self.session.exec(query).all()

        total_posts = sum(r.post_count for r in results)
        total_views = sum(r.total_views for r in results)
        total_reactions = sum(r.total_reactions for r in results)
        total_replies = sum(r.total_replies for r in results)
        total_forwards = sum(r.total_forwards for r in results)

        return {
            "channel_id": channel_id,
            "period_start": start_date,
            "period_end": end_date,
            "total_posts": total_posts,
            "total_views": total_views,
            "total_reactions": total_reactions,
            "total_replies": total_replies,
            "total_forwards": total_forwards,
            "daily_breakdown": [
                {
                    "message_date": r.message_date,
                    "post_count": r.post_count,
                    "total_views": r.total_views,
                    "total_reactions": r.total_reactions,
                    "total_replies": r.total_replies,
                    "total_forwards": r.total_forwards,
                }
                for r in results
            ]
        }

