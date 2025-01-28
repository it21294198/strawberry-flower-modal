import psycopg2
from psycopg2.extensions import connection as _connection
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Get the connection string components
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

# Get the connection string directly (if available)
db_connection_string = os.getenv(
    "DB_CONNECTION", 
    f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)

def get_db_connection() -> _connection:
    """Establish and return a database connection."""
    try:
        connection = psycopg2.connect(db_connection_string)
        return connection
    except Exception as e:
        raise RuntimeError(f"Error connecting to the database: {e}")

