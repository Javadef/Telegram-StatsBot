import os
from typing import Generator
from dotenv import load_dotenv
from sqlmodel import create_engine, Session

load_dotenv()

# --- CONFIGURATION ---
def get_db_url():
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASS')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    name = os.getenv('DB_NAME')
    dsn = os.getenv('DB_DSN')
    
    # Priority to full DSN, fallback to components, fallback to SQLite
    if dsn and "None" not in dsn:
        return dsn
    if user and password and host and name:
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"
    return "sqlite:///./telegram_channels.db"

DATABASE_URL = get_db_url()

# Create Engine
engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    from models import SQLModel # Import here to ensure models are registered
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session