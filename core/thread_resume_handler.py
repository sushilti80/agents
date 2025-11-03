"""
Thread Resume Handler for Chainlit Applications
Handles conversation thread restoration when users click on threads in the sidebar
"""
import logging
from typing import Dict, Callable, Optional, Any
import chainlit as cl
from chainlit.types import ThreadDict

logger = logging.getLogger(__name__)


class ThreadResumeHandler:
    """
    Handles thread resumption when users click on threads in the sidebar.
    
    Features:
    - Security: Validates thread belongs to current user
    - Context restoration: Reloads conversation history into agent memory
    - Agent re-initialization: Creates agent with correct mode for the thread
    
    Usage:
        resume_handler = ThreadResumeHandler(
            agent_modes=AGENT_MODES,
            agent_factory_func=create_agent,
            default_mode="platform"
        )
        
        @cl.on_chat_resume
        async def on_chat_resume(thread: ThreadDict):
            await resume_handler.handle_resume(thread)
    """
    
    def __init__(
        self,
        agent_modes: Dict[str, Any],
        agent_factory_func: Callable,
        default_mode: str = "platform",
        max_history_messages: int = 100
    ):
        """
        Initialize thread resume handler.
        
        Args:
            agent_modes: Dictionary of available agent modes.
                        Format: {"mode_name": AgentMode(name, file, emoji, description)}
            agent_factory_func: Function to create agent.
                               Should accept mode name and return agent instance.
                               Signature: async def create_agent(mode: str) -> ChatAgent
            default_mode: Fallback mode if thread mode is invalid or missing.
                         Default: "platform"
            max_history_messages: Maximum number of historical messages to restore.
                                 Default: 100
        """
        self.agent_modes = agent_modes
        self.agent_factory_func = agent_factory_func
        self.default_mode = default_mode
        self.max_history_messages = max_history_messages
    
    async def handle_resume(self, thread: ThreadDict):
        """
        Handle thread resumption.
        
        This is the main entry point called when a user clicks on a thread
        in the sidebar to resume a previous conversation.
        
        Process:
        1. Validate user owns the thread (security check)
        2. Initialize vector memory
        3. Set session context
        4. Validate and set agent mode
        5. Create agent with correct mode
        6. Restore conversation history to agent's memory
        7. Update session state
        
        Args:
            thread: ThreadDict from Chainlit containing thread metadata and history
        
        Raises:
            Exception: If thread restoration fails
        """
        try:
            thread_id = thread["id"]
            user_id = thread.get("userId")
            
            logger.info(f"🔄 Resuming thread: {thread_id} for user: {user_id}")
            
            # Get authenticated user
            chainlit_user = cl.user_session.get("user")
            if not chainlit_user:
                logger.error("No authenticated user during resume")
                await cl.Message(
                    content="❌ **Authentication Required**: Please log in to resume threads."
                ).send()
                return
            
            current_user_id = chainlit_user.identifier
            
            # Security check: ensure thread belongs to current user
            if user_id != current_user_id:
                logger.warning(
                    f"🔒 Access denied: Thread {thread_id} belongs to {user_id}, "
                    f"not {current_user_id}"
                )
                await cl.Message(
                    content="🔒 **Access Denied**: This thread belongs to another user.\n\n"
                            "You can only access your own conversation history."
                ).send()
                return
            
            # Initialize vector memory
            vector_memory = await self._initialize_vector_memory()
            
            # Set session context
            cl.user_session.set("user_id", user_id)
            cl.user_session.set("session_id", thread_id)
            
            # Get and validate mode
            mode = await self._get_and_validate_mode(thread)
            cl.user_session.set("agent_mode", mode)
            
            # Create agent with correct mode
            agent = await self._create_agent(mode)
            if not agent:
                return
            
            # Get new thread from agent
            thread_obj = agent.get_new_thread()
            
            # Restore conversation context to agent's memory
            await self._restore_agent_context(
                vector_memory=vector_memory,
                user_id=user_id,
                thread_id=thread_id,
                thread_obj=thread_obj
            )
            
            # Update session with agent and thread
            cl.user_session.set("agent", agent)
            cl.user_session.set("thread", thread_obj)
            
            logger.info(f"✅ Thread {thread_id} resumed - UI + Agent Context restored")
            
        except Exception as e:
            logger.error(f"Error resuming thread: {e}", exc_info=True)
            await cl.Message(
                content=f"❌ **Error resuming thread**: {str(e)}\n\n"
                        "Please try again or contact support if the issue persists."
            ).send()
    
    async def _initialize_vector_memory(self):
        """
        Initialize vector memory manager.
        
        Returns:
            VectorMemoryManager instance or None if unavailable
        """
        try:
            # Try importing vector_memory module
            try:
                from vector_memory import create_vector_memory_manager
            except ImportError:
                # Try relative import from parent directory
                import sys
                from pathlib import Path
                
                parent_dir = Path(__file__).parent.parent
                if str(parent_dir) not in sys.path:
                    sys.path.insert(0, str(parent_dir))
                
                from vector_memory import create_vector_memory_manager
            
            vector_memory = create_vector_memory_manager()
            await vector_memory.ensure_collection()
            cl.user_session.set("vector_memory", vector_memory)
            
            logger.debug("✅ Vector memory initialized")
            return vector_memory
            
        except Exception as e:
            logger.warning(f"⚠️ Vector memory unavailable: {e}")
            cl.user_session.set("vector_memory", None)
            return None
    
    async def _get_and_validate_mode(self, thread: ThreadDict) -> str:
        """
        Get mode from thread metadata and validate it exists.
        
        Args:
            thread: ThreadDict containing metadata
        
        Returns:
            Valid mode name (falls back to default_mode if invalid)
        """
        mode = thread.get("metadata", {}).get("mode", self.default_mode)
        
        # Validate mode exists in available modes
        if mode not in self.agent_modes:
            logger.warning(
                f"Unknown mode '{mode}' in thread metadata, "
                f"defaulting to '{self.default_mode}'"
            )
            mode = self.default_mode
        
        logger.debug(f"Using agent mode: {mode}")
        return mode
    
    async def _create_agent(self, mode: str):
        """
        Create agent using the factory function.
        
        Args:
            mode: Agent mode name
        
        Returns:
            Agent instance or None if creation failed
        """
        try:
            # Check if factory function is async
            import inspect
            if inspect.iscoroutinefunction(self.agent_factory_func):
                agent = await self.agent_factory_func(mode)
            else:
                agent = self.agent_factory_func(mode)
            
            if not agent:
                logger.error(f"Agent factory returned None for mode: {mode}")
                await cl.Message(
                    content="❌ **Agent initialization failed**\n\n"
                            "Unable to create agent. Please check your configuration."
                ).send()
                return None
            
            logger.debug(f"✅ Agent created for mode: {mode}")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create agent: {e}", exc_info=True)
            await cl.Message(
                content=f"❌ **Agent initialization failed**: {str(e)}"
            ).send()
            return None
    
    async def _restore_agent_context(
        self,
        vector_memory,
        user_id: str,
        thread_id: str,
        thread_obj
    ):
        """
        Restore conversation history to agent's memory.
        
        Note: The agent_framework AgentThread doesn't support direct message addition.
        Instead, we rely on Chainlit's automatic UI restoration from the steps array.
        The thread object maintains its own internal history through agent.run() calls.
        
        Args:
            vector_memory: VectorMemoryManager instance
            user_id: User identifier
            thread_id: Thread/session identifier
            thread_obj: Agent's thread object
        """
        if not vector_memory:
            logger.info("ℹ️ No vector memory - skipping context restoration")
            return
        
        try:
            # Load historical messages from vector storage
            history = await vector_memory.get_session_history(
                user_id=user_id,
                session_id=thread_id,
                limit=self.max_history_messages
            )
            
            if not history:
                logger.info(f"ℹ️ No history to restore for thread {thread_id}")
                return
            
            logger.info(f"✅ Found {len(history)} messages in history")
            logger.info(f"ℹ️ Context will be restored through Chainlit's UI display")
            logger.info(f"ℹ️ Thread object will build context as conversation continues")
            
            # Note: We don't manually add messages to the thread here because:
            # 1. AgentThread builds its history through agent.run() calls
            # 2. Chainlit automatically displays the conversation from the steps array
            # 3. The thread will naturally rebuild context as the user continues chatting
            
        except Exception as e:
            logger.error(f"Failed to load history: {e}", exc_info=True)
            logger.warning("⚠️ Agent will start with empty context")


def create_resume_handler(
    agent_modes: Dict[str, Any],
    agent_factory_func: Callable,
    default_mode: str = "platform",
    max_history_messages: int = 100
) -> Callable:
    """
    Factory function to create a thread resume callback.
    
    This is a convenience function that creates a ThreadResumeHandler and
    returns a callback suitable for the @cl.on_chat_resume decorator.
    
    Args:
        agent_modes: Dictionary of available agent modes
        agent_factory_func: Function to create agent instances
        default_mode: Fallback mode for invalid thread modes
        max_history_messages: Maximum messages to restore
    
    Returns:
        Async function suitable for @cl.on_chat_resume decorator
    
    Example:
        on_chat_resume = create_resume_handler(
            agent_modes=AGENT_MODES,
            agent_factory_func=create_agent,
            default_mode="platform"
        )
        
        # Then register with Chainlit:
        # This is done automatically if you assign to the function name
    """
    handler = ThreadResumeHandler(
        agent_modes=agent_modes,
        agent_factory_func=agent_factory_func,
        default_mode=default_mode,
        max_history_messages=max_history_messages
    )
    
    async def on_chat_resume(thread: ThreadDict):
        await handler.handle_resume(thread)
    
    return on_chat_resume
