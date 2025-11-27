import os
from dotenv import load_dotenv

load_dotenv()

def get_config():
    return {
        'API_ID': int(os.getenv('API_ID')),
        'API_HASH': os.getenv('API_HASH'),
        'BOT_TOKEN': os.getenv('BOT_TOKEN'),
        'DB_DSN': f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    }
