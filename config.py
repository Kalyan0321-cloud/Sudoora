import os
from dotenv import load_dotenv

load_dotenv()

# Render (and some other hosts) provide DATABASE_URL starting with "postgres://"
# but SQLAlchemy requires "postgresql://". Fix it transparently here.
def _get_db_uri():
    url = os.environ.get('DATABASE_URL', 'sqlite:///studyabroad.db')
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = _get_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API Keys
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')
    EXCHANGE_API_KEY = os.environ.get('EXCHANGE_API_KEY', '')

    # Mail config (optional)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')

    # Admin credentials
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
