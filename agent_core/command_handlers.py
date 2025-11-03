"""
Command handling and routing
Handles agent commands like /debug, /sessions, /session, /resume, mode switches
"""
import logging
from typing import Dict, List, Optional
import chainlit as cl

from .config import CommandConfig, DEFAULT_COMMAND_CONFIG, AgentMode
from .session_manager import SessionManager

logger = logging.getLogger(__name__)


class CommandRouter:
    """Routes and handles agent commands"""
    
    def __init__(
        self, 
        config: CommandConfig = None,
        session_manager: SessionManager = None
    ):
        """
        Initialize CommandRouter.
        
        Args:
            config: Command configuration (uses defaults if not provided)
            session_manager: SessionManager instance for session operations
        """
        self.config = config or DEFAULT_COMMAND_CONFIG
        self.session_manager = session_manager or SessionManager()
    
    async def route(
        self, 
        message: str, 
        vector_memory,
        user_id: str,
        available_modes: Dict[str, AgentMode]
    ) -> Optional[bool]:
        """
        Route a message to appropriate command handler.
        
        Args:
            message: User message
            vector_memory: Vector memory instance
            user_id: User ID
            available_modes: Dict of available agent modes
        
        Returns:
            True if command was handled, False if not a command, None if error
        """
        message_lower = message.lower().strip()
        
        # Debug command
        if message_lower in self.config.debug:
            await self.handle_debug(vector_memory, user_id)
            return True
        
        # List sessions command
        if message_lower in self.config.list_sessions:
            await self.handle_list_sessions(vector_memory, user_id)
            return True
        
        # Session info command
        if message_lower == self.config.session_info:
            await self.handle_session_info()
            return True
        
        # Resume command
        if message_lower.startswith(self.config.resume):
            await self.handle_resume(message_lower)
            return True
        
        # Mode switch commands
        for mode_name, mode in available_modes.items():
            if message_lower in [f"/mode {mode_name}", f"/switch {mode_name}"]:
                await self.handle_mode_switch(mode_name, mode)
                return True
        
        return False
    
    async def handle_debug(self, vector_memory, user_id: str) -> None:
        """
        Handle /debug command - shows session diagnostics.
        
        Args:
            vector_memory: Vector memory instance
            user_id: Current user ID
        """
        try:
            points, _ = await self.session_manager.query_all(vector_memory)
            
            # Aggregate by user
            user_sessions = {}
            for point in points:
                uid = point.payload.get("user_id", "unknown")
                user_sessions[uid] = user_sessions.get(uid, 0) + 1
            
            debug_info = [
                "🔍 **Debug Information**\n",
                f"**Current User ID:** `{user_id}`",
                f"**Total Points in Qdrant:** {len(points)}",
                f"**Users Found:** {len(user_sessions)}",
                "\n**Sessions by User:**"
            ]
            
            for uid, count in sorted(user_sessions.items(), key=lambda x: x[1], reverse=True):
                debug_info.append(f"  - `{uid}`: {count} messages")
            
            await cl.Message(content="\n".join(debug_info)).send()
            
        except Exception as e:
            logger.error(f"Debug command error: {e}")
            await cl.Message(content=f"❌ Debug command failed: {e}").send()
    
    async def handle_list_sessions(self, vector_memory, user_id: str) -> None:
        """
        Handle /sessions command - lists user's sessions.
        
        Args:
            vector_memory: Vector memory instance
            user_id: Current user ID
        """
        try:
            points, _ = await self.session_manager.query_by_user(vector_memory, user_id)
            
            if not points:
                await cl.Message(content="No previous sessions found.").send()
                return
            
            sessions = self.session_manager.aggregate_sessions(points)
            
            session_list = ["📚 **Your Sessions**\n"]
            for sid, info in sorted(
                sessions.items(), 
                key=lambda x: x[1]["last_timestamp"], 
                reverse=True
            ):
                short_id = sid.replace("session_", "")[:8]
                session_list.append(
                    f"**{short_id}** ({info['count']} messages) - {info['mode']}\n"
                    f"  Last: {info['last_message'][:60]}..."
                )
            
            await cl.Message(content="\n".join(session_list)).send()
            
        except Exception as e:
            logger.error(f"List sessions error: {e}")
            await cl.Message(content=f"❌ Failed to list sessions: {e}").send()
    
    async def handle_session_info(self) -> None:
        """Handle /session command - shows current session ID and mode"""
        session_id = cl.user_session.get("session_id") or cl.user_session.get("id")
        user_id = cl.user_session.get("user_id", "anonymous")
        agent_mode = cl.user_session.get("agent_mode", "unknown")
        
        # Try to get mode emoji and name if available
        mode_display = agent_mode
        try:
            # Check if we have AGENT_MODES in the session or can import it
            from ..daedalus import AGENT_MODES
            mode_info = AGENT_MODES.get(agent_mode, {})
            if hasattr(mode_info, 'emoji') and hasattr(mode_info, 'name'):
                mode_display = f"{mode_info.emoji} {mode_info.name}"
            elif isinstance(mode_info, dict):
                emoji = mode_info.get("emoji", "🤖")
                name = mode_info.get("name", agent_mode)
                mode_display = f"{emoji} {name}"
        except:
            # Fallback to just showing the mode string
            pass
        
        info = [
            "ℹ️ **Current Session**\n",
            f"**Session ID:** `{session_id}`",
            f"**User ID:** `{user_id}`",
            f"**Agent Mode:** {mode_display}"
        ]
        
        await cl.Message(content="\n".join(info)).send()
    
    async def handle_resume(self, message: str) -> None:
        """
        Handle /resume command - placeholder for session resumption.
        
        Args:
            message: Resume command with optional session ID
        """
        parts = message.split()
        if len(parts) > 1:
            session_id = parts[1]
            await cl.Message(
                content=f"🔄 Resuming session `{session_id}` (use session browser for full restoration)"
            ).send()
        else:
            await cl.Message(
                content="Usage: `/resume <session_id>` or use the session browser"
            ).send()
    
    async def handle_mode_switch(self, mode_name: str, mode: AgentMode) -> None:
        """
        Handle mode switch commands.
        
        Args:
            mode_name: Name of the mode to switch to
            mode: AgentMode instance
        """
        cl.user_session.set("current_mode", mode_name)
        await cl.Message(
            content=f"{mode.emoji} **Switched to {mode.name} mode**\n{mode.description}"
        ).send()


# Standalone functions for backward compatibility
async def handle_debug_command(vector_memory, user_id: str) -> None:
    """Handle /debug command"""
    router = CommandRouter()
    await router.handle_debug(vector_memory, user_id)


async def handle_list_sessions_command(vector_memory, user_id: str) -> None:
    """Handle /sessions command"""
    router = CommandRouter()
    await router.handle_list_sessions(vector_memory, user_id)


async def handle_session_info_command() -> None:
    """Handle /session command"""
    router = CommandRouter()
    await router.handle_session_info()


async def handle_mode_switch(mode_name: str, mode: AgentMode) -> None:
    """Handle mode switch"""
    router = CommandRouter()
    await router.handle_mode_switch(mode_name, mode)
