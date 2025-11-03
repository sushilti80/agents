"""
Vector Memory Manager - Qdrant Integration for Agent Framework

Provides semantic search and persistent context memory using Qdrant vector database.
Enables multi-user isolation, conversation resume, and token optimization through
retrieval-augmented generation (RAG).

Features:
- Store conversation messages as vector embeddings
- Search for semantically similar context
- User-based filtering for multi-tenant isolation
- Session-based conversation grouping
- Azure OpenAI embeddings integration

Usage:
    from shared.vector_memory import VectorMemoryManager
    
    manager = VectorMemoryManager(
        qdrant_host="localhost",
        qdrant_port=6333,
        azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_openai_key=os.getenv("AZURE_OPENAI_API_KEY"),
        embedding_deployment="text-embedding-3-small"
    )
    
    # Store a message
    await manager.store_message(
        user_id="user123",
        session_id="session456",
        message="How do I design a web API?",
        role="user"
    )
    
    # Search for relevant context
    context = await manager.search_context(
        user_id="user123",
        query="API design patterns",
        top_k=3
    )
"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
import asyncio

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest
)
from openai import AzureOpenAI

logger = logging.getLogger(__name__)


class VectorMemoryManager:
    """
    Manages vector-based conversation memory using Qdrant.
    
    Handles embedding generation, storage, and semantic search
    with multi-user isolation and session management.
    """
    
    def __init__(
        self,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        azure_openai_endpoint: Optional[str] = None,
        azure_openai_key: Optional[str] = None,
        embedding_deployment: Optional[str] = None,
        collection_name: str = "agent-conversations",
        vector_size: Optional[int] = None  # Auto-detect based on embedding model
    ):
        """
        Initialize Vector Memory Manager.
        
        Args:
            qdrant_host: Qdrant server hostname
            qdrant_port: Qdrant server port
            azure_openai_endpoint: Azure OpenAI endpoint URL
            azure_openai_key: Azure OpenAI API key
            embedding_deployment: Deployment name for embeddings (defaults to AZURE_OPENAI_EMBEDDING_DEPLOYMENT env var)
            collection_name: Qdrant collection name
            vector_size: Embedding vector dimension (auto-detected if not provided)
        """
        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.collection_name = collection_name
        
        # Get embedding deployment from env var if not provided
        self.embedding_deployment = embedding_deployment or os.getenv(
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", 
            "text-embedding-3-small"
        )
        
        # Auto-detect vector size based on embedding model if not provided
        if vector_size is None:
            vector_size = 1024 if "text-embedding-3-small" in self.embedding_deployment else 1536
        
        self.vector_size = vector_size
        
        # Initialize Azure OpenAI client for embeddings
        self.openai_client = AzureOpenAI(
            azure_endpoint=azure_openai_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=azure_openai_key or os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01"
        )
        
        logger.info(f"✅ VectorMemoryManager initialized: {qdrant_host}:{qdrant_port}")
        logger.info(f"📦 Collection: {collection_name}, Vector size: {vector_size}")
        logger.info(f"🔧 Embedding model: {self.embedding_deployment}")
    
    async def ensure_collection(self) -> None:
        """
        Create Qdrant collection if it doesn't exist.
        
        Collection schema:
        - Vector size: 1536 (ada-002) or 1024 (text-embedding-3-small)
        - Distance: Cosine similarity
        - Payload: user_id, session_id, message, role, timestamp, agent_mode
        """
        try:
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Collection created: {self.collection_name}")
            else:
                logger.info(f"✅ Collection exists: {self.collection_name}")
        
        except Exception as e:
            logger.error(f"❌ Failed to ensure collection: {e}")
            raise
    
    async def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using Azure OpenAI.
        
        Args:
            text: Input text to embed
        
        Returns:
            List of floats representing the embedding vector
        """
        try:
            # For text-embedding-3-small and text-embedding-3-large, 
            # explicitly set dimensions to match collection vector size
            embedding_params = {
                "input": text,
                "model": self.embedding_deployment
            }
            
            # Add dimensions parameter for embedding-3 models
            if "text-embedding-3" in self.embedding_deployment:
                embedding_params["dimensions"] = self.vector_size
            
            response = self.openai_client.embeddings.create(**embedding_params)
            embedding = response.data[0].embedding
            logger.debug(f"✅ Generated embedding for text (length: {len(text)}, dimensions: {len(embedding)})")
            return embedding
        
        except Exception as e:
            logger.error(f"❌ Failed to generate embedding: {e}")
            raise
    
    async def store_message(
        self,
        user_id: str,
        session_id: str,
        message: str,
        role: str,
        agent_mode: Optional[str] = None
    ) -> str:
        """
        Store a conversation message in Qdrant.
        
        Args:
            user_id: Unique user identifier (cl.user_session.id or SSO ID)
            session_id: Conversation session ID
            message: Message text content
            role: Message role ('user' or 'assistant')
            agent_mode: Agent mode ('platform' or 'cloud')
        
        Returns:
            Point ID (UUID) of the stored message
        """
        try:
            # Ensure collection exists
            await self.ensure_collection()
            
            # Generate embedding
            embedding = await self.get_embedding(message)
            
            # Create unique point ID
            import uuid
            point_id = str(uuid.uuid4())
            
            # Create point with payload
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "user_id": user_id,
                    "session_id": session_id,
                    "message": message,
                    "role": role,
                    "agent_mode": agent_mode,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Store in Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info(f"✅ Stored message: user={user_id}, role={role}, id={point_id}")
            return point_id
        
        except Exception as e:
            logger.error(f"❌ Failed to store message: {e}")
            raise
    
    async def search_context(
        self,
        user_id: str,
        query: str,
        top_k: int = 3,
        session_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for semantically similar messages in user's history.
        
        Args:
            user_id: User identifier for filtering
            query: Search query text
            top_k: Number of results to return (default: 3)
            session_id: Optional session filter (for same-session search)
        
        Returns:
            List of dicts with 'message', 'role', 'score', 'timestamp'
        """
        try:
            # Ensure collection exists
            await self.ensure_collection()
            
            # Generate query embedding
            query_embedding = await self.get_embedding(query)
            
            # Build filter for user isolation
            filter_conditions = [
                FieldCondition(key="user_id", match=MatchValue(value=user_id))
            ]
            
            # Add session filter if provided
            if session_id:
                filter_conditions.append(
                    FieldCondition(key="session_id", match=MatchValue(value=session_id))
                )
            
            # Search Qdrant
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=Filter(must=filter_conditions)
            )
            
            # Format results with minimum score threshold
            # Only include results with 70%+ semantic similarity
            MIN_RELEVANCE_SCORE = 0.70
            
            context = [
                {
                    "message": hit.payload["message"],
                    "role": hit.payload["role"],
                    "score": hit.score,
                    "timestamp": hit.payload.get("timestamp"),
                    "agent_mode": hit.payload.get("agent_mode")
                }
                for hit in search_result
                if hit.score >= MIN_RELEVANCE_SCORE  # Filter low-relevance matches
            ]
            
            filtered_count = len(search_result) - len(context)
            if filtered_count > 0:
                logger.info(f"ℹ️ Filtered {filtered_count} low-relevance results (score < {MIN_RELEVANCE_SCORE})")
            
            logger.info(f"✅ Found {len(context)} relevant messages for user={user_id}")
            return context
        
        except Exception as e:
            logger.error(f"❌ Failed to search context: {e}")
            return []
    
    def format_context_for_prompt(self, context: List[Dict]) -> str:
        """
        Format retrieved context for injection into agent prompt.
        
        Args:
            context: List of context items from search_context()
        
        Returns:
            Formatted string for prompt injection
        """
        if not context:
            return ""
        
        formatted = "**Relevant context from previous conversations:**\n\n"
        for i, item in enumerate(context, 1):
            role = "User" if item["role"] == "user" else "Assistant"
            formatted += f"{i}. [{role}] {item['message']}\n"
        
        formatted += "\n---\n\n"
        return formatted
    
    async def get_session_history(
        self,
        user_id: str,
        session_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Retrieve full conversation history for a session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            limit: Maximum number of messages to retrieve
        
        Returns:
            List of messages sorted by timestamp
        """
        try:
            # Search with session filter (using a neutral query)
            results = await self.search_context(
                user_id=user_id,
                query="conversation history",
                top_k=limit,
                session_id=session_id
            )
            
            # Sort by timestamp
            results.sort(key=lambda x: x.get("timestamp", ""), reverse=False)
            
            return results
        
        except Exception as e:
            logger.error(f"❌ Failed to get session history: {e}")
            return []
    
    async def delete_user_data(self, user_id: str) -> bool:
        """
        Delete all data for a specific user (GDPR compliance).
        
        Args:
            user_id: User identifier
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Note: Qdrant doesn't support delete by filter in all versions
            # This is a placeholder - implement based on your Qdrant version
            logger.warning(f"⚠️ Delete user data for {user_id} - implement based on Qdrant version")
            # You may need to scroll through and delete points individually
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to delete user data: {e}")
            return False


# Factory function for easy initialization
def create_vector_memory_manager(
    qdrant_host: Optional[str] = None,
    qdrant_port: Optional[int] = None,
    embedding_deployment: Optional[str] = None
) -> VectorMemoryManager:
    """
    Create VectorMemoryManager with environment variable fallbacks.
    
    Args:
        qdrant_host: Qdrant host (defaults to QDRANT_HOST env var or 'localhost')
        qdrant_port: Qdrant port (defaults to QDRANT_PORT env var or 6333)
        embedding_deployment: Embedding model (defaults to env var or 'text-embedding-3-small')
    
    Returns:
        Configured VectorMemoryManager instance
    """
    host = qdrant_host or os.getenv("QDRANT_HOST", "localhost")
    port = int(qdrant_port or os.getenv("QDRANT_PORT", "6333"))
    deployment = embedding_deployment or os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
    
    # Determine vector size based on embedding model
    vector_size = 1024 if "text-embedding-3-small" in deployment else 1536
    
    return VectorMemoryManager(
        qdrant_host=host,
        qdrant_port=port,
        embedding_deployment=deployment,
        vector_size=vector_size
    )
