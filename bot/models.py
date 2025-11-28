from datetime import date, datetime
from typing import Optional, List, TypedDict
from sqlmodel import SQLModel, Field
from sqlalchemy import BigInteger, UniqueConstraint, Date

# --- TYPING FOR REPOSITORY INPUTS ---

class ChannelData(TypedDict, total=False):
    """Data dictionary for upserting a Channel."""
    channel_id: int
    title: str
    username: Optional[str]
    description: Optional[str]
    photo_file_id: Optional[str]
    subscriber_count: Optional[int]
    type: Optional[str]
    linked_chat_id: Optional[int]

class MessageData(TypedDict):
    """Data dictionary for bulk upserting Messages."""
    channel_id: int
    message_id: int
    date: datetime
    views: int
    reactions: int
    replies: int
    forwards: int
    # Add other fields as needed

class DailyMetrics(TypedDict):
    """Metrics for a single day."""
    posts: int
    views: int
    reactions: int # EXTENSIBILITY
    replies: int   # EXTENSIBILITY
    forwards: int  # EXTENSIBILITY

# --- DATABASE MODELS ---

class Channel(SQLModel, table=True):
    __tablename__ = "channels"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    channel_id: int = Field(sa_type=BigInteger, unique=True, nullable=False)
    username: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)      # NEW
    photo_file_id: Optional[str] = Field(default=None)    # NEW: profile pic Telegram ID
    subscriber_count: Optional[int] = Field(default=0)    # NEW
    type: Optional[str] = Field(default=None)            # public/private
    linked_chat_id: Optional[int] = Field(default=None, sa_type=BigInteger)   # linked discussion group
    added_at: datetime = Field(default_factory=datetime.utcnow)

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    __table_args__ = (UniqueConstraint("channel_id", "message_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    channel_id: int = Field(sa_type=BigInteger, nullable=False)
    message_id: int = Field(sa_type=BigInteger, nullable=False)
    date: datetime = Field(nullable=False)
    views: Optional[int] = Field(default=0)
    reactions: Optional[int] = Field(default=0)
    replies: Optional[int] = Field(default=0)
    forwards: Optional[int] = Field(default=0)

# ⚠️ EXTENSIBILITY FIX: Added reaction, replies, forwards fields to ChannelStatsDaily
class ChannelStatsDaily(SQLModel, table=True):
    __tablename__ = "channel_stats_daily"
    __table_args__ = (UniqueConstraint("channel_id", "message_date"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    channel_id: int = Field(sa_type=BigInteger, nullable=False)
    message_date: date = Field(sa_type=Date, nullable=False)
    post_count: int = Field(default=0)
    total_views: int = Field(default=0)
    total_reactions: int = Field(default=0)
    total_replies: int = Field(default=0)
    total_forwards: int = Field(default=0)

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
    # NEW FIELDS:
    total_reactions: int 
    total_replies: int
    total_forwards: int
    daily_breakdown: List[dict]