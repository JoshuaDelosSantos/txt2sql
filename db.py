import psycopg2
from config import settings

def get_connection():
    """Establish a connection to the PostgreSQL database."""
    settings.require_db()
    
    return psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password
    )