"""Initialize databases with required schemas and indexes."""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
from database.postgres import PostgresDB
from database.mongodb import MongoDB
from database.redis_db import RedisDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_databases():
    """Initialize all databases."""
    logger.info("Initializing databases...")
    logger.info("Note: Make sure Docker Compose is running (docker-compose up -d)")
    logger.info("")
    
    success_count = 0
    total_count = 3
    
    try:
        # PostgreSQL - tables are created automatically in __init__
        logger.info("Initializing PostgreSQL...")
        postgres = PostgresDB()
        logger.info("✓ PostgreSQL initialized")
        success_count += 1
    except Exception as e:
        logger.warning(f"⚠ PostgreSQL initialization failed: {e}")
        logger.info("  → Make sure PostgreSQL is running: docker-compose up -d postgres")
    
    try:
        # MongoDB - indexes are created automatically in __init__
        logger.info("Initializing MongoDB...")
        mongodb = MongoDB()
        logger.info("✓ MongoDB initialized")
        success_count += 1
    except Exception as e:
        logger.warning(f"⚠ MongoDB initialization failed: {e}")
        logger.info("  → Make sure MongoDB is running: docker-compose up -d mongodb")
    
    try:
        # Redis - no initialization needed
        logger.info("Initializing Redis...")
        redis_db = RedisDB()
        logger.info("✓ Redis initialized")
        success_count += 1
    except Exception as e:
        logger.warning(f"⚠ Redis initialization failed: {e}")
        logger.info("  → Make sure Redis is running: docker-compose up -d redis")
    
    logger.info("")
    logger.info(f"Database initialization complete! ({success_count}/{total_count} databases connected)")
    
    if success_count < total_count:
        logger.info("")
        logger.info("To start all databases, run:")
        logger.info("  docker-compose up -d")
        logger.info("")
        logger.info("Then run this script again to initialize the databases.")


if __name__ == "__main__":
    init_databases()

