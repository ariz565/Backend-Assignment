# Database utilities for connection checking and initialization
import time
from models.database import init_db, check_db_connection
from config import Config

def initialize_database():
    # Database initialization with retry mechanism using config settings
    max_retries = Config.DATABASE_CONNECTION_RETRIES
    retry_delay = Config.DATABASE_RETRY_DELAY
    
    for attempt in range(max_retries):
        try:
            print(f"Attempting database connection (attempt {attempt + 1}/{max_retries})")
            
            # Check if database is accessible
            if check_db_connection():
                print("✅ Database connection successful")
                
                # Initialize database tables
                init_db()
                print("✅ Database tables initialized")
                return True
            else:
                raise Exception("Database connection failed")
                
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("❌ Failed to initialize database after all retries")
                return False
    
    return False
