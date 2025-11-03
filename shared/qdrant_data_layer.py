"""
Chainlit Data Layer Implementation for Qdrant Vector Memory
This makes our Qdrant sessions appear in Chainlit's native left sidebar.

NOTE: This file has been moved to shared/ directory for better code organization.
It is imported by agent_core/data_layer_factory.py
"""
import logging
from typing import Optional, Dict, List, Any
from chainlit.data import BaseDataLayer
from chainlit.types import (
    ThreadDict, 
    PaginatedResponse, 
    Pagination, 
    ThreadFilter
)
from chainlit import PersistedUser, User
from literalai.helper import utc_now
from qdrant_client.models import Filter, FieldCondition, MatchValue
from shared.vector_memory import VectorMemoryManager
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class QdrantDataLayer(BaseDataLayer):
    """
    Custom data layer that integrates Qdrant vector storage with Chainlit's thread UI.
    This enables the left sidebar thread history to work with our existing Qdrant sessions.
    """
    
    def __init__(self, vector_memory: VectorMemoryManager):
        """
        Initialize the data layer with vector memory manager.
        
        Args:
            vector_memory: The VectorMemoryManager instance for Qdrant storage
        """
        self.vector_memory = vector_memory
        logger.info("✅ QdrantDataLayer initialized")
    
    async def get_user(self, identifier: str) -> Optional[PersistedUser]:
        """
        Get user by identifier (email).
        Since we use OAuth, we just return a PersistedUser object.
        """
        try:
            return PersistedUser(
                id=identifier,
                createdAt=utc_now(),
                identifier=identifier
            )
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    async def create_user(self, user: User) -> Optional[PersistedUser]:
        """
        Create a new user.
        Since we use OAuth, users are auto-created on first login.
        """
        try:
            return PersistedUser(
                id=user.identifier,
                createdAt=utc_now(),
                identifier=user.identifier,
                metadata=user.metadata
            )
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    async def list_threads(
        self, 
        pagination: Pagination, 
        filters: ThreadFilter
    ) -> PaginatedResponse[ThreadDict]:
        """
        List all threads (sessions) for a user.
        This populates the left sidebar with session history.
        
        Args:
            pagination: Pagination parameters (cursor, first/last)
            filters: Filter by user_id, search, etc.
        
        Returns:
            Paginated list of threads
        """
        try:
            user_id = filters.userId
            if not user_id:
                logger.warning("No user_id provided in filters")
                return PaginatedResponse(
                    data=[],
                    pageInfo={"hasNextPage": False, "startCursor": None, "endCursor": None}
                )
            
            # Query Qdrant for all sessions belonging to this user
            scroll_filter = Filter(
                must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
            )
            
            # Get all points for this user
            search_result = self.vector_memory.qdrant_client.scroll(
                collection_name=self.vector_memory.collection_name,
                scroll_filter=scroll_filter,
                limit=1000,  # Get all sessions
                with_payload=True,
                with_vectors=False
            )
            
            # Group by session_id and extract session metadata
            sessions_map = {}
            for point in search_result[0]:
                payload = point.payload
                session_id = payload.get("session_id")
                
                if not session_id:
                    continue
                
                if session_id not in sessions_map:
                    # First message in this session
                    timestamp = payload.get("timestamp")
                    created_at = datetime.fromisoformat(timestamp) if timestamp else utc_now()
                    
                    # Generate smart title from first user message
                    message = payload.get("message", "")
                    role = payload.get("role", "")
                    
                    # Try to get first user message for title
                    title = None
                    if role == "user" and message:
                        # Smart title: remove common prefixes and truncate
                        title = self._generate_smart_title(message)
                    
                    # If no good title, use timestamp instead of session ID
                    if not title:
                        # Format: "Chat - Nov 01, 10:30"
                        title = f"Chat - {created_at.strftime('%b %d, %H:%M')}"
                    
                    sessions_map[session_id] = {
                        "id": session_id,
                        "name": title,
                        "createdAt": created_at.isoformat(),
                        "userId": user_id,
                        "userIdentifier": user_id,
                        "steps": [],
                        "metadata": {
                            "mode": payload.get("mode", "chat"),
                            "session_id": session_id
                        },
                        "tags": [payload.get("mode", "chat")],
                        "_first_timestamp": created_at,
                        "_message_count": 0
                    }
                
                # Update message count
                sessions_map[session_id]["_message_count"] += 1
                
                # Update title if we find a better user message
                # If current title is timestamp-based "Chat - ...", replace it with actual message
                if role == "user" and payload.get("message"):
                    current_title = sessions_map[session_id]["name"]
                    # Replace if:
                    # 1. Current title starts with "Chat -" (timestamp fallback)
                    # 2. Current title is very short (poor quality)
                    if current_title.startswith("Chat -") or len(current_title) < 10:
                        new_title = self._generate_smart_title(payload.get("message"))
                        if new_title and len(new_title) > 5:  # Valid new title
                            sessions_map[session_id]["name"] = new_title
                            logger.debug(f"Updated thread title: '{current_title}' -> '{new_title}'")
            
            # Convert to list and sort by creation time (newest first)
            threads = list(sessions_map.values())
            threads.sort(key=lambda x: x["_first_timestamp"], reverse=True)
            
            # Remove internal tracking fields
            for thread in threads:
                del thread["_first_timestamp"]
                del thread["_message_count"]
            
            logger.info(f"📋 Found {len(threads)} threads for user {user_id}")
            
            # Simple pagination (no cursor support yet)
            return PaginatedResponse(
                data=threads,
                pageInfo={
                    "hasNextPage": False,
                    "startCursor": None,
                    "endCursor": None
                }
            )
            
        except Exception as e:
            logger.error(f"Error listing threads: {e}", exc_info=True)
            return PaginatedResponse(
                data=[],
                pageInfo={"hasNextPage": False, "startCursor": None, "endCursor": None}
            )
    
    def _generate_smart_title(self, message: str) -> str:
        """Generate a smart title from a user message"""
        if not message or not message.strip():
            return ""
        
        message = message.strip()
        
        # Remove common prefixes (case insensitive)
        prefixes_to_remove = [
            "can you ", "could you ", "please ", "help me ", 
            "i need ", "i want ", "how do i ", "how to ",
            "what is ", "what are ", "explain ", "tell me ",
            "show me ", "give me ", "i would like "
        ]
        
        message_lower = message.lower()
        for prefix in prefixes_to_remove:
            if message_lower.startswith(prefix):
                message = message[len(prefix):].strip()
                # Capitalize first letter
                if message:
                    message = message[0].upper() + message[1:]
                break
        
        # Remove trailing punctuation for cleaner titles
        message = message.rstrip('?.!')
        
        # Truncate intelligently at word boundary
        max_length = 50
        if len(message) > max_length:
            # Try to break at sentence or clause
            truncated = message[:max_length]
            # Look for good break points
            for break_char in ['.', ',', ';', ' -', ' ']:
                last_break = truncated.rfind(break_char)
                if last_break > max_length * 0.6:  # At least 60% of max length
                    truncated = truncated[:last_break]
                    break
            else:
                # No good break point, break at last space
                last_space = truncated.rfind(' ')
                if last_space > 0:
                    truncated = truncated[:last_space]
            return truncated.strip() + "..."
        
        return message
    
    async def get_thread(self, thread_id: str) -> Optional[ThreadDict]:
        """
        Get a specific thread by ID.
        This is called when user clicks on a thread in the sidebar.
        """
        try:
            # Query Qdrant for this session
            scroll_filter = Filter(
                must=[FieldCondition(key="session_id", match=MatchValue(value=thread_id))]
            )
            
            search_result = self.vector_memory.qdrant_client.scroll(
                collection_name=self.vector_memory.collection_name,
                scroll_filter=scroll_filter,
                limit=1000,
                with_payload=True,
                with_vectors=False
            )
            
            if not search_result[0]:
                return None
            
            # Build thread from points
            messages = []
            user_id = None
            created_at = None
            mode = "chat"
            
            for point in search_result[0]:
                payload = point.payload
                user_id = payload.get("user_id")
                
                timestamp = payload.get("timestamp")
                msg_time = datetime.fromisoformat(timestamp) if timestamp else utc_now()
                
                if created_at is None or msg_time < created_at:
                    created_at = msg_time
                
                mode = payload.get("mode", "chat")
                
                messages.append({
                    "role": payload.get("role"),
                    "message": payload.get("message"),
                    "timestamp": timestamp
                })
            
            # Sort messages by timestamp
            messages.sort(key=lambda x: x["timestamp"])
            
            # Generate title from first user message
            title = None
            for msg in messages:
                if msg["role"] == "user":
                    title = self._generate_smart_title(msg["message"])
                    break
            
            # Convert messages to Chainlit steps format
            steps = []
            for idx, msg in enumerate(messages):
                step = {
                    "id": f"{thread_id}_step_{idx}",
                    "name": msg["role"],
                    "type": "user_message" if msg["role"] == "user" else "assistant_message",
                    "threadId": thread_id,
                    "output": msg["message"],
                    "createdAt": msg["timestamp"],
                    "start": msg["timestamp"],
                    "end": msg["timestamp"],
                    "generation": None,
                    "showInput": False,
                    "waitForAnswer": False,
                    "isError": False,
                    "metadata": {},
                    "tags": []
                }
                steps.append(step)
            
            thread = {
                "id": thread_id,
                "name": title or f"Session {thread_id[:8]}",
                "createdAt": created_at.isoformat() if created_at else utc_now(),
                "userId": user_id,
                "userIdentifier": user_id,
                "steps": steps,  # Now populated with actual message steps
                "metadata": {
                    "mode": mode,
                    "session_id": thread_id,
                    "message_count": len(messages)
                },
                "tags": [mode]
            }
            
            return thread
            
        except Exception as e:
            logger.error(f"Error getting thread: {e}", exc_info=True)
            return None
    
    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ):
        """
        Update thread metadata.
        Currently, our Qdrant implementation doesn't support thread-level updates,
        but we log the intent for future implementation.
        """
        logger.info(f"Thread update requested for {thread_id}: name={name}, metadata={metadata}, tags={tags}")
        # Note: Qdrant stores messages, not thread metadata
        # To implement this, we'd need a separate metadata collection
        pass
    
    async def delete_thread(self, thread_id: str):
        """
        Delete a thread (session) and all its messages.
        """
        try:
            # Delete all points with this session_id
            self.vector_memory.qdrant_client.delete(
                collection_name=self.vector_memory.collection_name,
                points_selector=Filter(
                    must=[FieldCondition(key="session_id", match=MatchValue(value=thread_id))]
                )
            )
            logger.info(f"✅ Deleted thread {thread_id}")
        except Exception as e:
            logger.error(f"Error deleting thread: {e}", exc_info=True)
    
    async def get_thread_author(self, thread_id: str) -> str:
        """Get the author (user_id) of a thread"""
        try:
            scroll_filter = Filter(
                must=[FieldCondition(key="session_id", match=MatchValue(value=thread_id))]
            )
            
            search_result = self.vector_memory.qdrant_client.scroll(
                collection_name=self.vector_memory.collection_name,
                scroll_filter=scroll_filter,
                limit=1,
                with_payload=True,
                with_vectors=False
            )
            
            if search_result[0]:
                return search_result[0][0].payload.get("user_id", "unknown")
            
            return "unknown"
            
        except Exception as e:
            logger.error(f"Error getting thread author: {e}")
            return "unknown"
    
    # ========================================
    # Step/Message Management
    # ========================================
    
    async def create_step(self, step_dict: Dict[str, Any]):
        """
        Create a new step (message) in a thread.
        This is called automatically by Chainlit when messages are sent.
        """
        try:
            # Extract thread and user info
            thread_id = step_dict.get("threadId")
            user_id = step_dict.get("userId")  # This might not be present
            
            # Our vector memory uses add_message for storage
            # Chainlit will call this, but we're already storing via add_message
            logger.debug(f"Step created: thread={thread_id}, type={step_dict.get('type')}")
            
        except Exception as e:
            logger.error(f"Error creating step: {e}")
    
    async def get_steps(self, thread_id: str) -> List[Dict[str, Any]]:
        """Get all steps (messages) in a thread"""
        # Not currently used by our implementation
        return []
    
    async def delete_step(self, step_id: str):
        """Delete a specific step"""
        logger.debug(f"Step delete requested: {step_id}")
        pass
    
    # ========================================
    # Feedback & Elements (optional features)
    # ========================================
    
    async def upsert_feedback(self, feedback: Dict[str, Any]) -> str:
        """Store user feedback on messages"""
        logger.debug(f"Feedback received: {feedback}")
        return str(uuid.uuid4())
    
    async def delete_feedback(self, feedback_id: str) -> bool:
        """Delete feedback"""
        return True
    
    async def create_element(self, element: Dict[str, Any]):
        """Create an element (file, image, etc.)"""
        logger.debug(f"Element created: {element.get('name')}")
        pass
    
    async def get_element(
        self, thread_id: str, element_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get an element by ID"""
        return None
    
    async def delete_element(self, element_id: str, thread_id: Optional[str] = None):
        """Delete an element"""
        pass
    
    # ========================================
    # Additional Required Methods
    # ========================================
    
    async def update_step(self, step_dict: Dict[str, Any]):
        """
        Update an existing step/message.
        Called when a message is edited or updated.
        """
        logger.debug(f"Step update requested: {step_dict.get('id')}")
        # Not implemented - our Qdrant storage is append-only
        pass
    
    async def build_debug_url(self) -> str:
        """
        Build a debug URL for the data layer.
        This is used for debugging and monitoring.
        """
        # Return Qdrant dashboard URL if available
        try:
            qdrant_url = self.vector_memory.qdrant_client._client.rest_uri
            return f"{qdrant_url}/dashboard"
        except:
            return "http://localhost:6333/dashboard"
    
    async def close(self):
        """
        Close the data layer and cleanup resources.
        Called when the application shuts down.
        """
        logger.info("🔌 Closing QdrantDataLayer...")
        try:
            # Qdrant client will be closed automatically
            # Nothing specific to cleanup here
            pass
        except Exception as e:
            logger.error(f"Error closing data layer: {e}")
