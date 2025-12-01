from typing import List, Optional, Dict
from datetime import date, datetime
from sqlmodel import Session, select, func, col
from sqlalchemy import asc
from models import Channel, Message, ChannelStatsDaily, ScrapeRun
from models import ChannelData, MessageData, DailyMetrics 

class TelegramRepository:
    def __init__(self, session: Session):
        self.session = session

    def upsert_channel(self, channel_data: ChannelData) -> Channel:
        with self.session:
            channel = self.session.exec(
                select(Channel).where(Channel.channel_id == channel_data['channel_id'])
            ).first()
            
            if channel:
                for key, value in channel_data.items():
                    if key != 'channel_id':
                        setattr(channel, key, value) 
                self.session.add(channel)
            else:
                channel = Channel(**channel_data) 
                self.session.add(channel)
                
            self.session.commit()
            self.session.refresh(channel)
            return channel

    def upsert_messages(self, messages_data: List[MessageData]):
        if not messages_data:
            return

        # 1. Try High-Performance PostgreSQL Upsert
        try:
            from sqlalchemy.dialects.postgresql import insert
            
            data_to_insert = [dict(msg) for msg in messages_data]
            stmt = insert(Message).values(data_to_insert)
            
            # Map columns to update on conflict
            update_cols = {
                "views": stmt.excluded.views,
                "reactions": stmt.excluded.reactions,
                "replies": stmt.excluded.replies,
                "forwards": stmt.excluded.forwards,
                "date": stmt.excluded.date 
            }
            
            stmt = stmt.on_conflict_do_update(
                index_elements=[Message.channel_id, Message.message_id],
                set_=update_cols
            )
            
            with self.session:
                self.session.execute(stmt)
                self.session.commit()

        except (ImportError, Exception) as e:
            # 2. Fallback: Standard SQLModel Merge (Slower but reliable)
            # This fixes the "updates not saved" bug.
            # session.merge() checks primary key; if exists, it UPDATES. If not, it INSERTS.
            with self.session:
                for msg_data in messages_data:
                    # We manually construct the object to merge
                    # Note: We must query to find the primary key 'id' if we want to merge properly 
                    # without purely relying on the unique constraint, but simpler here:
                    
                    # Safer Fallback approach: Check existence manually
                    existing = self.session.exec(
                        select(Message).where(
                            Message.channel_id == msg_data['channel_id'],
                            Message.message_id == msg_data['message_id']
                        )
                    ).first()

                    if existing:
                        # UPDATE
                        existing.views = msg_data['views']
                        existing.reactions = msg_data['reactions']
                        existing.replies = msg_data['replies']
                        existing.forwards = msg_data['forwards']
                        self.session.add(existing)
                    else:
                        # INSERT
                        self.session.add(Message(**msg_data))
                
                self.session.commit()

    def update_daily_stats(self, channel_id: int, stats_buffer: Dict[date, DailyMetrics]):
            dates_to_update = list(stats_buffer.keys())
            
            with self.session:
                for day in dates_to_update:
                    start_of_day = datetime.combine(day, datetime.min.time())
                    end_of_day = datetime.combine(day, datetime.max.time())

                    # Use coalesce to ensure DB returns 0 instead of None
                    statement = select(
                        func.count(Message.id).label("posts"),
                        func.coalesce(func.sum(Message.views), 0).label("views"),
                        func.coalesce(func.sum(Message.reactions), 0).label("reactions"),
                        func.coalesce(func.sum(Message.replies), 0).label("replies"),
                        func.coalesce(func.sum(Message.forwards), 0).label("forwards")
                    ).where(
                        Message.channel_id == channel_id,
                        Message.date >= start_of_day,
                        Message.date <= end_of_day
                    )

                    result = self.session.exec(statement).first()
                    
                    # Unpack directly (safe because of coalesce)
                    posts, views, reactions, replies, forwards = result

                    # Update Logic
                    daily_stat = self.session.exec(
                        select(ChannelStatsDaily).where(
                            ChannelStatsDaily.channel_id == channel_id,
                            ChannelStatsDaily.message_date == day
                        )
                    ).first()

                    if daily_stat:
                        daily_stat.post_count = posts
                        daily_stat.total_views = views
                        daily_stat.total_reactions = reactions
                        daily_stat.total_replies = replies
                        daily_stat.total_forwards = forwards
                        self.session.add(daily_stat)
                    else:
                        new_stat = ChannelStatsDaily(
                            channel_id=channel_id,
                            message_date=day,
                            post_count=posts,
                            total_views=views,
                            total_reactions=reactions,
                            total_replies=replies,
                            total_forwards=forwards
                        )
                        self.session.add(new_stat)
                
                self.session.commit()

    # ... The rest of your methods (get_last_scraped_id, update_scrape_run, etc.) remain the same ...
    def get_last_scraped_id(self, channel_id: int) -> Optional[int]:
        run = self.session.exec(select(ScrapeRun).where(ScrapeRun.channel_id == channel_id)).first()
        return run.last_scraped_id if run else None

    def update_scrape_run(self, channel_id: int, last_id: int):
        with self.session:
            run = self.session.exec(select(ScrapeRun).where(ScrapeRun.channel_id == channel_id)).first()
            if run:
                if last_id > (run.last_scraped_id or 0):
                    run.last_scraped_id = last_id
                run.last_scraped_at = datetime.utcnow()
            else:
                run = ScrapeRun(channel_id=channel_id, last_scraped_id=last_id, last_scraped_at=datetime.utcnow())
            self.session.add(run)
            self.session.commit()

    def get_all_channels(self) -> List[Channel]:
        return self.session.exec(select(Channel)).all()

    def get_channel_by_id(self, pk_id: int) -> Optional[Channel]:
        return self.session.get(Channel, pk_id)

    def get_analytics(self, channel_id: int, start_date: date, end_date: date) -> Dict:
        query = select(ChannelStatsDaily).where(
            ChannelStatsDaily.channel_id == channel_id,
            ChannelStatsDaily.message_date >= start_date,
            ChannelStatsDaily.message_date <= end_date
        ).order_by(asc(ChannelStatsDaily.message_date))

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
                    "date": r.message_date,
                    "posts": r.post_count,
                    "views": r.total_views,
                    "reactions": r.total_reactions,
                    "replies": r.total_replies,
                    "forwards": r.total_forwards,
                }
                for r in results
            ]
        }

    def get_messages_by_channel(self, channel_id: int, limit: int = 100, offset: int = 0) -> List[Message]:
        query = select(Message)\
            .where(Message.channel_id == channel_id)\
            .order_by(Message.message_id)\
            .offset(offset)\
            .limit(limit)
        return self.session.exec(query).all()