"""PostgreSQL database connection and operations."""
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from typing import Optional, Dict, Any
from config.settings import settings
import json
import logging

logger = logging.getLogger(__name__)

# Optional Redis import for caching
try:
    from database.redis_db import RedisDB
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    RedisDB = None


class PostgresDB:
    """PostgreSQL database handler for structured application data."""
    
    def __init__(self):
        self.pool = None
        self._initialize_pool()
        self._create_tables()
        # Initialize Redis for caching if available
        self.redis_cache = None
        if REDIS_AVAILABLE:
            try:
                self.redis_cache = RedisDB()
                logger.info("Redis cache initialized for PostgreSQL operations")
            except Exception as e:
                logger.warning(f"Redis cache not available: {e}")
                self.redis_cache = None
    
    def _initialize_pool(self):
        """Initialize connection pool."""
        try:
            self.pool = SimpleConnectionPool(
                1, 20,
                host=settings.postgres_host,
                port=settings.postgres_port,
                database=settings.postgres_db,
                user=settings.postgres_user,
                password=settings.postgres_password
            )
            logger.info("PostgreSQL connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool."""
        conn = self.pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            self.pool.putconn(conn)
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Applications table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS applications (
                        id SERIAL PRIMARY KEY,
                        application_id VARCHAR(50) UNIQUE NOT NULL,
                        applicant_name VARCHAR(255),
                        applicant_id VARCHAR(50),
                        status VARCHAR(50) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata JSONB
                    )
                """)
                
                # Eligibility assessments table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS eligibility_assessments (
                        id SERIAL PRIMARY KEY,
                        application_id VARCHAR(50) REFERENCES applications(application_id),
                        income_level VARCHAR(50),
                        employment_status VARCHAR(50),
                        family_size INTEGER,
                        wealth_score DECIMAL(10, 2),
                        eligibility_score DECIMAL(5, 2),
                        recommendation VARCHAR(50),
                        reasoning TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Add unique constraint if table exists but constraint doesn't
                try:
                    cur.execute("""
                        DO $$ 
                        BEGIN
                            IF NOT EXISTS (
                                SELECT 1 FROM pg_constraint 
                                WHERE conname = 'eligibility_assessments_application_id_key'
                            ) THEN
                                ALTER TABLE eligibility_assessments 
                                ADD CONSTRAINT eligibility_assessments_application_id_key 
                                UNIQUE (application_id);
                            END IF;
                        EXCEPTION
                            WHEN undefined_table THEN
                                NULL;
                        END $$;
                    """)
                except Exception as e:
                    logger.debug(f"Constraint check: {e}")
        
                conn.commit()
                logger.info("PostgreSQL tables created/verified")
    
    def create_application(self, application_data: Dict[str, Any]) -> str:
        """Create a new application record."""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Convert metadata dict to JSON for JSONB column
                metadata = application_data.get("metadata", {})
                metadata_json = Json(metadata) if metadata else None
                
                cur.execute("""
                    INSERT INTO applications (application_id, applicant_name, applicant_id, metadata)
                    VALUES (%s, %s, %s, %s)
                    RETURNING application_id
                """, (
                    application_data.get("application_id"),
                    application_data.get("applicant_name"),
                    application_data.get("applicant_id"),
                    metadata_json
                ))
                result = cur.fetchone()
                return result["application_id"]
    
    def get_application(self, application_id: str) -> Optional[Dict[str, Any]]:
        """Get application by ID."""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT * FROM applications WHERE application_id = %s
                    """, (application_id,))
                    result = cur.fetchone()
                    if result:
                        app_dict = dict(result)
                        # Handle metadata JSONB field
                        if "metadata" in app_dict and app_dict["metadata"]:
                            if isinstance(app_dict["metadata"], str):
                                try:
                                    app_dict["metadata"] = json.loads(app_dict["metadata"])
                                except:
                                    app_dict["metadata"] = {}
                        return app_dict
                    return None
        except Exception as e:
            logger.error(f"Error getting application: {e}")
            return None
    
    def update_application_status(self, application_id: str, status: str):
        """Update application status."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE applications 
                    SET status = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE application_id = %s
                """, (status, application_id))
    
    def save_eligibility_assessment(self, assessment_data: Dict[str, Any]):
        """Save eligibility assessment results and invalidate cache."""
        application_id = assessment_data.get("application_id")
        cache_key = f"eligibility:{application_id}"
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # First, try to delete existing assessment for this application
                    cur.execute("""
                        DELETE FROM eligibility_assessments 
                        WHERE application_id = %s
                    """, (application_id,))
                    
                    # Then insert new assessment
                    cur.execute("""
                        INSERT INTO eligibility_assessments 
                        (application_id, income_level, employment_status, family_size, 
                         wealth_score, eligibility_score, recommendation, reasoning)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        assessment_data.get("application_id"),
                        assessment_data.get("income_level"),
                        assessment_data.get("employment_status"),
                        assessment_data.get("family_size"),
                        assessment_data.get("wealth_score"),
                        assessment_data.get("eligibility_score"),
                        assessment_data.get("recommendation"),
                        assessment_data.get("reasoning")
                    ))
            
            # Invalidate cache after saving
            if self.redis_cache:
                try:
                    self.redis_cache.delete_cache(cache_key)
                    logger.debug(f"Invalidated cache for eligibility assessment: {application_id}")
                except Exception as e:
                    logger.warning(f"Redis cache invalidation error: {e}")
                    
        except Exception as e:
            logger.error(f"Error saving eligibility assessment: {e}", exc_info=True)
            # Try alternative approach without ON CONFLICT
            try:
                with self.get_connection() as conn:
                    with conn.cursor() as cur:
                        # Delete existing
                        cur.execute("""
                            DELETE FROM eligibility_assessments 
                            WHERE application_id = %s
                        """, (application_id,))
                        
                        # Insert new
                        cur.execute("""
                            INSERT INTO eligibility_assessments 
                            (application_id, income_level, employment_status, family_size, 
                             wealth_score, eligibility_score, recommendation, reasoning)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            assessment_data.get("application_id"),
                            assessment_data.get("income_level"),
                            assessment_data.get("employment_status"),
                            assessment_data.get("family_size"),
                            assessment_data.get("wealth_score"),
                            assessment_data.get("eligibility_score"),
                            assessment_data.get("recommendation"),
                            assessment_data.get("reasoning")
                        ))
                
                # Invalidate cache after saving
                if self.redis_cache:
                    try:
                        self.redis_cache.delete_cache(cache_key)
                    except Exception as e:
                        logger.warning(f"Redis cache invalidation error: {e}")
            except Exception as e2:
                logger.error(f"Failed to save eligibility assessment after retry: {e2}")
                raise
    
    def get_eligibility_assessment(self, application_id: str) -> Optional[Dict[str, Any]]:
        """Get eligibility assessment for an application with Redis caching."""
        cache_key = f"eligibility:{application_id}"
        
        # Try to get from cache first
        if self.redis_cache:
            try:
                cached = self.redis_cache.get_cache(cache_key)
                if cached:
                    logger.debug(f"Cache hit for eligibility assessment: {application_id}")
                    return cached
            except Exception as e:
                logger.warning(f"Redis cache read error: {e}")
        
        # Cache miss - get from database
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT * FROM eligibility_assessments 
                        WHERE application_id = %s
                        ORDER BY created_at DESC
                        LIMIT 1
                    """, (application_id,))
                    result = cur.fetchone()
                    if result:
                        assessment = dict(result)
                        # Convert Decimal to float for JSON serialization
                        if "eligibility_score" in assessment and assessment["eligibility_score"] is not None:
                            assessment["eligibility_score"] = float(assessment["eligibility_score"])
                        if "wealth_score" in assessment and assessment["wealth_score"] is not None:
                            assessment["wealth_score"] = float(assessment["wealth_score"])
                        
                        # Cache the result (TTL: 1 hour)
                        if self.redis_cache:
                            try:
                                self.redis_cache.set_cache(cache_key, assessment, ttl=3600)
                                logger.debug(f"Cached eligibility assessment: {application_id}")
                            except Exception as e:
                                logger.warning(f"Redis cache write error: {e}")
                        
                        return assessment
                    return None
        except Exception as e:
            logger.error(f"Error getting eligibility assessment: {e}")
            return None
    
    def save_final_recommendation(self, application_id: str, recommendation_data: Dict[str, Any]):
        """Save final recommendation to application metadata."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get current metadata
                    cur.execute("""
                        SELECT metadata FROM applications WHERE application_id = %s
                    """, (application_id,))
                    result = cur.fetchone()
                    
                    # Handle metadata extraction safely
                    if result:
                        if hasattr(result, '__getitem__') and len(result) > 0:
                            current_metadata = result[0]
                        elif hasattr(result, '__iter__'):
                            current_metadata = list(result)[0] if result else {}
                        else:
                            current_metadata = result[0] if result else {}
                    else:
                        current_metadata = {}
                    
                    # Handle JSONB field - might be dict or string
                    if isinstance(current_metadata, str):
                        try:
                            current_metadata = json.loads(current_metadata)
                        except json.JSONDecodeError:
                            current_metadata = {}
                    
                    if not isinstance(current_metadata, dict):
                        current_metadata = {}
                    
                    # Update metadata with final recommendation
                    current_metadata["final_recommendation"] = recommendation_data
                    
                    cur.execute("""
                        UPDATE applications 
                        SET metadata = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE application_id = %s
                    """, (Json(current_metadata), application_id))
        except Exception as e:
            logger.error(f"Error saving final recommendation: {e}", exc_info=True)
            # Don't raise - allow application to continue
    
    def get_final_recommendation(self, application_id: str) -> Optional[Dict[str, Any]]:
        """Get final recommendation from application metadata."""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT metadata FROM applications WHERE application_id = %s
                    """, (application_id,))
                    result = cur.fetchone()
                    if result:
                        # Handle RealDictRow
                        if hasattr(result, 'metadata'):
                            metadata = result.metadata
                        elif isinstance(result, dict):
                            metadata = result.get("metadata")
                        else:
                            metadata = result[0] if result else None
                        
                        if not metadata:
                            return None
                        
                        # Handle JSONB field - it might be a dict or string
                        if isinstance(metadata, str):
                            try:
                                metadata = json.loads(metadata)
                            except json.JSONDecodeError:
                                logger.warning(f"Could not parse metadata JSON: {metadata}")
                                return None
                        
                        if isinstance(metadata, dict):
                            recommendation = metadata.get("final_recommendation")
                            if not recommendation:
                                return None
                            
                            # Ensure recommendation is a dict
                            if not isinstance(recommendation, dict):
                                return None
                            
                            # Convert any Decimal values to float
                            if "support_amount" in recommendation and recommendation["support_amount"] is not None:
                                try:
                                    recommendation["support_amount"] = float(recommendation["support_amount"])
                                except (ValueError, TypeError):
                                    recommendation["support_amount"] = 0
                            
                            if "confidence" in recommendation and recommendation["confidence"] is not None:
                                try:
                                    recommendation["confidence"] = float(recommendation["confidence"])
                                except (ValueError, TypeError):
                                    recommendation["confidence"] = 0.0
                            
                            return recommendation
                    return None
        except Exception as e:
            logger.error(f"Error getting final recommendation: {e}", exc_info=True)
            return None

