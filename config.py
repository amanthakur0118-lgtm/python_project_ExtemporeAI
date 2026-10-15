import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'extempore-ai-secret-key-2026')
    
    # MySQL Database Settings
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'extempore_db')
    
    # Enable automatic SQLite fallback if MySQL is not configured/unreachable
    ALLOW_SQLITE_FALLBACK = os.environ.get('ALLOW_SQLITE_FALLBACK', 'true').lower() in ('true', '1', 'yes')
    if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        SQLITE_PATH = '/tmp/extempore_backup.db'
    else:
        SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'extempore_backup.db')
    
    # AI / LLM Settings
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY', '')
    
    # News Feed API Key (Optional; public RSS feeds are used by default)
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')
