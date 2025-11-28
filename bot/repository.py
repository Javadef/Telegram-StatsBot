from typing import List, Optional, Dict
from datetime import date, datetime
from sqlmodel import Session, select, col, and_
from sqlalchemy import func
from models import Channel, Message, ChannelStatsDaily, ScrapeRun

class TelegramRepository:
    def __init__(self, session: Session):
        self.session = session

    def upsert_channel(self, channel_id: int, title: str, username: Optional[str]) -> Channel:
        channel = self.session.exec(select(Channel).where(Channel.channel_id == channel_id)).first()
        if channel:
            channel.title = title
            channel.username = username
            self.session.add(channel)
        else:
            channel = Channel(channel_id=channel_id, title=title, username=username)
            self.session.add(channel)
        self.session.commit()
        self.session.refresh(channel)
        return channel

    def upsert_messages(self, messages_data: List[Dict]):
        if not messages_data:
            return
        
        # In a high-throughput scenario, prefer sqlalchemy.dialects.postgresql.insert for bulk upsert
        # For this implementation, we check existence to ensure safety with SQLModel
        for msg in messages_data:
            existing = self.session.exec(
                select(Message).where(
                    Message.channel_id == msg['channel_id'], 
                    Message.message_id == msg['message_id']
                )
            ).first()
            
            if existing:
                existing.views = msg['views']
                self.session.add(existing)
            else:
                new_msg = Message(**msg)
                self.session.add(new_msg)
        self.session.commit()

    def update_daily_stats(self, channel_id: int, stats_buffer: Dict[date, Dict]):
        for date_key, metrics in stats_buffer.items():
            stats = self.session.exec(
                select(ChannelStatsDaily).where(
                    ChannelStatsDaily.channel_id == channel_id, 
                    ChannelStatsDaily.message_date == date_key  # <-- FIXED
                )
            ).first()

            if stats:
                stats.post_count += metrics['posts']
                stats.total_views += metrics['views']
            else:
                stats = ChannelStatsDaily(
                    channel_id=channel_id, 
                    message_date=date_key,          # <-- FIXED
                    post_count=metrics['posts'], 
                    total_views=metrics['views']
                )
            self.session.add(stats)
        self.session.commit()


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

    def get_analytics(self, channel_id: int, start_date: date, end_date: date) -> Dict:
        query = select(ChannelStatsDaily).where(
            ChannelStatsDaily.channel_id == channel_id,
            ChannelStatsDaily.date >= start_date,
            ChannelStatsDaily.date <= end_date
        ).order_by(ChannelStatsDaily.date)
        
        results = self.session.exec(query).all()
        
        total_posts = sum(r.post_count for r in results)
        total_views = sum(r.total_views for r in results)
        
        return {
            "channel_id": channel_id,
            "period_start": start_date,
            "period_end": end_date,
            "total_posts": total_posts,
            "total_views": total_views,
            "daily_breakdown": [r.model_dump() for r in results]
        }