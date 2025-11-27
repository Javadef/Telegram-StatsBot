from datetime import datetime, date
from typing import Optional, List
from sqlmodel import SQLModel, Field
from sqlalchemy import BigInteger, UniqueConstraint

# --- DATABASE MODELS ---

class Channel(SQLModel, table=True):
    __tablename__ = "channels"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    channel_id: int = Field(sa_type=BigInteger, unique=True, nullable=False)
    username: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    added_at: datetime = Field(default_factory=datetime.utcnow)

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    __table_args__ = (UniqueConstraint("channel_id", "message_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    channel_id: int = Field(sa_type=BigInteger, nullable=False)
    message_id: int = Field(sa_type=BigInteger, nullable=False)
    date: datetime = Field(nullable=False)
    views: Optional[int] = Field(default=0)

class ChannelStatsDaily(SQLModel, table=True):
    __tablename__ = "channel_stats_daily"
    __table_args__ = (UniqueConstraint("channel_id", "date"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    channel_id: int = Field(sa_type=BigInteger, nullable=False)
    date: date = Field(nullable=False)
    post_count: int = Field(default=0)
    total_views: int = Field(default=0)

class ScrapeRun(SQLModel, table=True):
    __tablename__ = "scrape_runs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    channel_id: int = Field(sa_type=BigInteger, unique=True, nullable=False)
    last_scraped_id: Optional[int] = Field(default=None, sa_type=BigInteger)
    last_scraped_at: datetime = Field(default_factory=datetime.utcnow)

# --- API REQUEST/RESPONSE SCHEMAS ---

class ScrapeRequest(SQLModel):
    channel_identifier: str
    start_date: date
    end_date: Optional[date] = None

class ScrapeStatusResponse(SQLModel):
    channel_identifier: str
    status: str  # 'running', 'completed', 'failed'
    messages_processed: int
    current_message_date: Optional[datetime] = None
    error: Optional[str] = None

class AnalyticsResponse(SQLModel):
    channel_id: int
    period_start: date
    period_end: date
    total_posts: int
    total_views: int
    daily_breakdown: List[dict]