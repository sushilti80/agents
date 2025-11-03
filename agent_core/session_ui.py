"""
Session UI components
Handles session browser, restoration, and user-facing session management UI
"""
import logging
from typing import List, Dict, Optional, Callable
from datetime import datetime
import chainlit as cl

from .config import SessionConfig, DEFAULT_SESSION_CONFIG, AgentMode
from .session_manager import SessionManager, extract_short_id
from .utils import get_mode_emoji

logger = logging.getLogger(__name__)


class SessionUI:
    """Manages session-related UI components"""
    
    def __init__(
        self, 
        config: SessionConfig = None,
        session_manager: SessionManager = None
    ):
        """
        Initialize SessionUI.
        
        Args:
            config: Session configuration (uses defaults if not provided)
            session_manager: SessionManager instance for session operations
        """
        self.config = config or DEFAULT_SESSION_CONFIG
        self.session_manager = session_manager or SessionManager()
    
    async def display_browser(
        self, 
        vector_memory,
        user_id: str,
        mode_emojis: Dict[str, str]
    ) -> None:
        """
        Display session browser with clickable actions.
        
        Args:
            vector_memory: Vector memory instance
            user_id: Current user ID
            mode_emojis: Dict mapping mode names to emojis
        """
        try:
            points, _ = await self.session_manager.query_by_user(vector_memory, user_id)
            
            if not points:
                logger.info(f"No sessions found for user {user_id}")
                return
            
            sessions = self.session_manager.aggregate_sessions(points)
            
            # Sort by last timestamp (most recent first)
            sorted_sessions = sorted(
                sessions.items(),
                key=lambda x: x[1]["last_timestamp"],
                reverse=True
            )[:self.config.max_sessions_display]
            
            if not sorted_sessions:
                return
            
            # Create actions for each session
            actions = []
            for session_id, info in sorted_sessions:
                short_id = extract_short_id(session_id, self.config.short_id_length)
                mode_emoji = get_mode_emoji(info["mode"], mode_emojis)
                
                # Format timestamp
                try:
                    ts = datetime.fromisoformat(info["last_timestamp"])
                    time_str = ts.strftime("%b %d, %H:%M")
                except:
                    time_str = "Unknown time"
                
                # Truncate last message
                last_msg = info["last_message"][:50] + "..." if len(info["last_message"]) > 50 else info["last_message"]
                
                action = cl.Action(
                    name=f"restore_{session_id}",
                    value=session_id,
                    label=f"{mode_emoji} {short_id} • {info['count']} msgs • {time_str}",
                    description=last_msg
                )
                actions.append(action)
            
            # Display browser message
            msg = cl.Message(
                content=f"📚 **Previous Sessions** (showing {len(actions)} most recent)\n"
                        f"Click a session to restore:"
            )
            msg.actions = actions
            await msg.send()
            
        except Exception as e:
            logger.error(f"Session browser error: {e}")
    
    async def restore_by_id(
        self, 
        vector_memory,
        session_id: str,
        current_session_id: str,
        agent_factory_func: Optional[Callable] = None
    ) -> bool:
        """
        Restore a specific session by ID.
        
        Args:
            vector_memory: Vector memory instance
            session_id: Session ID to restore
            current_session_id: Current Chainlit session ID
            agent_factory_func: Optional function to recreate agent with correct mode.
                               Should accept mode name and return agent instance.
        
        Returns:
            True if restoration successful, False otherwise
        """
        try:
            # Ensure proper format
            if not session_id.startswith(self.config.session_id_prefix):
                session_id = f"{self.config.session_id_prefix}{session_id}"
            
            # Query session messages
            points, _ = await self.session_manager.query_by_id(vector_memory, session_id)
            
            if not points:
                await cl.Message(content=f"❌ Session `{session_id}` not found").send()
                return False
            
            # Sort messages by timestamp
            messages = sorted(
                [p.payload for p in points],
                key=lambda x: x.get("timestamp", "")
            )
            
            if not messages:
                await cl.Message(content=f"❌ No messages in session `{session_id}`").send()
                return False
            
            # Display restoration header
            short_id = extract_short_id(session_id, self.config.short_id_length)
            await cl.Message(
                content=f"🔄 **Restoring session `{short_id}`** ({len(messages)} messages)"
            ).send()
            
            # Extract agent_mode from first message (for mode restoration)
            agent_mode = messages[0].get("agent_mode", "platform") if messages else "platform"
            
            # Replay messages in UI
            for msg in messages[-self.config.max_history_messages:]:
                role = msg.get("role", "user")
                content = msg.get("message", "")
                
                if role == "user":
                    await cl.Message(content=f"**You:** {content}", author="User").send()
                else:
                    await cl.Message(content=content, author="Assistant").send()
            
            # Update session state (including agent mode)
            cl.user_session.set("restored_from", session_id)
            cl.user_session.set("id", current_session_id)  # Keep current session ID
            cl.user_session.set("agent_mode", agent_mode)  # Restore agent mode from session
            
            # Recreate agent with correct mode if factory function provided
            if agent_factory_func:
                try:
                    # Check if factory function is async
                    import inspect
                    if inspect.iscoroutinefunction(agent_factory_func):
                        agent = await agent_factory_func(mode_name=agent_mode)
                    else:
                        agent = agent_factory_func(mode_name=agent_mode)
                    
                    if agent:
                        thread = agent.get_new_thread()
                        cl.user_session.set("agent", agent)
                        cl.user_session.set("thread", thread)
                        logger.info(f"✅ Recreated agent in {agent_mode} mode")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to recreate agent: {e}")
            
            await cl.Message(
                content=f"✅ Session restored in **{agent_mode}** mode.\n"
                        f"Continuing in current session `{current_session_id}`"
            ).send()
            
            return True
            
        except Exception as e:
            logger.error(f"Session restoration error: {e}")
            await cl.Message(content=f"❌ Failed to restore session: {e}").send()
            return False
    
    async def find_and_restore(
        self,
        vector_memory,
        user_id: str,
        session_hint: str,
        current_session_id: str
    ) -> bool:
        """
        Find a session by partial ID and restore it.
        
        Args:
            vector_memory: Vector memory instance
            user_id: User ID for filtering
            session_hint: Partial session ID or hint
            current_session_id: Current Chainlit session ID
        
        Returns:
            True if restoration successful, False otherwise
        """
        try:
            points, _ = await self.session_manager.query_by_user(vector_memory, user_id)
            
            # Find matching session
            matching_session = None
            for point in points:
                sid = point.payload.get("session_id", "")
                if session_hint in sid:
                    matching_session = sid
                    break
            
            if matching_session:
                return await self.restore_by_id(vector_memory, matching_session, current_session_id)
            else:
                await cl.Message(content=f"❌ No session matching `{session_hint}` found").send()
                return False
                
        except Exception as e:
            logger.error(f"Find and restore error: {e}")
            return False


# Standalone functions for backward compatibility
async def display_session_browser(
    vector_memory,
    user_id: str,
    mode_emojis: Dict[str, str]
) -> None:
    """Display session browser"""
    ui = SessionUI()
    await ui.display_browser(vector_memory, user_id, mode_emojis)


async def restore_session_by_id(
    vector_memory,
    session_id: str,
    current_session_id: str,
    agent_factory_func: Optional[Callable] = None
) -> bool:
    """
    Restore a specific session.
    
    Args:
        vector_memory: Vector memory instance
        session_id: Session ID to restore
        current_session_id: Current session ID
        agent_factory_func: Optional function to recreate agent with correct mode
    
    Returns:
        True if successful, False otherwise
    """
    ui = SessionUI()
    return await ui.restore_by_id(
        vector_memory, 
        session_id, 
        current_session_id,
        agent_factory_func
    )


async def find_and_restore_session(
    vector_memory,
    user_id: str,
    session_hint: str,
    current_session_id: str
) -> bool:
    """Find and restore a session by hint"""
    ui = SessionUI()
    return await ui.find_and_restore(vector_memory, user_id, session_hint, current_session_id)
