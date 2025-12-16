"""MongoDB database connection and operations."""
from pymongo import MongoClient
from pymongo.database import Database
from typing import Dict, Any, Optional, List
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB handler for unstructured document data."""
    
    def __init__(self):
        self.client = MongoClient(settings.mongodb_uri)
        self.db: Database = self.client[settings.mongodb_db]
        self._create_indexes()
    
    def _create_indexes(self):
        """Create necessary indexes."""
        try:
            self.db.documents.create_index("application_id")
            self.db.documents.create_index("document_type")
            self.db.extracted_data.create_index("application_id")
            logger.info("MongoDB indexes created")
        except Exception as e:
            logger.error(f"Error creating MongoDB indexes: {e}")
    
    def store_document(self, application_id: str, document_type: str, 
                      document_data: Dict[str, Any]) -> str:
        """Store document data in MongoDB."""
        try:
            doc = {
                "application_id": application_id,
                "document_type": document_type,
                "data": document_data,
                "created_at": document_data.get("created_at")
            }
            result = self.db.documents.insert_one(doc)
            logger.info(f"Document stored: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error storing document: {e}")
            raise
    
    def get_documents(self, application_id: str, 
                     document_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve documents for an application."""
        query = {"application_id": application_id}
        if document_type:
            query["document_type"] = document_type
        
        try:
            documents = list(self.db.documents.find(query))
            for doc in documents:
                doc["_id"] = str(doc["_id"])
            return documents
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def store_extracted_data(self, application_id: str, 
                            extracted_data: Dict[str, Any]):
        """Store extracted data from documents."""
        try:
            doc = {
                "application_id": application_id,
                "extracted_data": extracted_data,
                "created_at": extracted_data.get("created_at")
            }
            self.db.extracted_data.insert_one(doc)
            logger.info(f"Extracted data stored for {application_id}")
        except Exception as e:
            logger.error(f"Error storing extracted data: {e}")
            raise
    
    def get_extracted_data(self, application_id: str) -> Optional[Dict[str, Any]]:
        """Get extracted data for an application."""
        try:
            result = self.db.extracted_data.find_one({"application_id": application_id})
            if result:
                result["_id"] = str(result["_id"])
            return result
        except Exception as e:
            logger.error(f"Error retrieving extracted data: {e}")
            return None

