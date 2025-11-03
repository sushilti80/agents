"""
Session management core functionality
Handles Qdrant queries, session aggregation, and session ID utilities
"""
import logging
from typing import List, Dict, Tuple, Optional
from qdrant_client.models import Filter, FieldCondition, MatchValue

from .config import SessionConfig, DEFAULT_SESSION_CONFIG
from .utils import format_session_id as _format_session_id, extract_short_id as _extract_short_id

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages session queries and operations with Qdrant vector store"""
    
    def __init__(self, config: SessionConfig = None):
        """
        Initialize SessionManager.
        
        Args:
            config: Session configuration (uses defaults if not provided)
        """
        self.config = config or DEFAULT_SESSION_CONFIG
    
    async def query_by_user(
        self, 
        vector_memory, 
        user_id: str, 
        limit: Optional[int] = None
    ) -> List[Tuple]:
        """
        Query Qdrant for sessions filtered by user_id.
        
        Args:
            vector_memory: Vector memory manager instance
            user_id: User identifier
            limit: Maximum sessions to query (uses config default if not provided)
        
        Returns:
            List of (points, _) tuples from Qdrant scroll()
        """
        query_limit = limit or self.config.max_sessions_query
        
        return vector_memory.qdrant_client.scroll(
            collection_name=vector_memory.collection_name,
            scroll_filter=Filter(
                must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
            ),
            limit=query_limit,
            with_payload=True,
            with_vectors=False
        )
    
    async def query_all(
        self, 
        vector_memory, 
        limit: Optional[int] = None
    ) -> List[Tuple]:
        """
        Query Qdrant for ALL sessions (no filter). Used for debugging.
        
        Args:
            vector_memory: Vector memory manager instance
            limit: Maximum sessions to query (uses config default if not provided)
        
        Returns:
            List of (points, _) tuples from Qdrant scroll()
        """
        query_limit = limit or self.config.max_sessions_query
        
        return vector_memory.qdrant_client.scroll(
            collection_name=vector_memory.collection_name,
            limit=query_limit,
            with_payload=True,
            with_vectors=False
        )
    
    async def query_by_id(self, vector_memory, session_id: str) -> List[Tuple]:
        """
        Query Qdrant for a specific session by ID.
        
        Args:
            vector_memory: Vector memory manager instance
            session_id: Session identifier
        
        Returns:
            List of (points, _) tuples from Qdrant scroll()
        """
        return vector_memory.qdrant_client.scroll(
            collection_name=vector_memory.collection_name,
            scroll_filter=Filter(
                must=[FieldCondition(key="session_id", match=MatchValue(value=session_id))]
            ),
            limit=1,
            with_payload=True,
            with_vectors=False
        )
    
    def aggregate_sessions(self, points: List) -> Dict[str, Dict]:
        """
        Aggregate Qdrant points into session summaries.
        
        Args:
            points: List of Qdrant points
        
        Returns:
            Dict of {session_id: {count, last_timestamp, mode, user_id, last_message}}
        """
        sessions = {}
        
        for point in points:
            session_id = point.payload.get("session_id")
            if not session_id:
                continue
            
            if session_id not in sessions:
                sessions[session_id] = {
                    "count": 0,
                    "last_timestamp": point.payload.get("timestamp", ""),
                    "mode": point.payload.get("agent_mode", "unknown"),
                    "user_id": point.payload.get("user_id", ""),
                    "last_message": ""
                }
            
            sessions[session_id]["count"] += 1
            
            # Keep most recent timestamp and message
            current_ts = point.payload.get("timestamp", "")
            if current_ts > sessions[session_id]["last_timestamp"]:
                sessions[session_id]["last_timestamp"] = current_ts
                sessions[session_id]["last_message"] = point.payload.get("message", "")[:100]
        
        return sessions


# Standalone functions for backward compatibility
async def query_sessions_by_user(
    vector_memory, 
    user_id: str, 
    limit: int = 100
) -> List[Tuple]:
    """Query Qdrant for sessions filtered by user_id"""
    manager = SessionManager()
    return await manager.query_by_user(vector_memory, user_id, limit)


async def query_all_sessions(
    vector_memory, 
    limit: int = 100
) -> List[Tuple]:
    """Query Qdrant for ALL sessions"""
    manager = SessionManager()
    return await manager.query_all(vector_memory, limit)


async def query_session_by_id(
    vector_memory, 
    session_id: str
) -> List[Tuple]:
    """Query Qdrant for a specific session by ID"""
    manager = SessionManager()
    return await manager.query_by_id(vector_memory, session_id)


def aggregate_sessions(points: List) -> Dict[str, Dict]:
    """Aggregate Qdrant points into session summaries"""
    manager = SessionManager()
    return manager.aggregate_sessions(points)


def format_session_id(session_id: str, prefix: str = "session_") -> str:
    """Ensure session ID has proper prefix"""
    return _format_session_id(session_id, prefix)


def extract_short_id(session_id: str, length: int = 8) -> str:
    """Extract short readable ID from full session ID"""
    return _extract_short_id(session_id, length)
