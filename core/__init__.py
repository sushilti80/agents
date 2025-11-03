"""
Agent Core Library
Reusable components for building multi-agent systems with Chainlit and Qdrant

Version 1.1.0 - Added SSO/OAuth and Data Layer support
"""

# Configuration
from .config import (
    AgentMode,
    SessionConfig,
    CommandConfig,
    AgentConfig,
    DEFAULT_SESSION_CONFIG,
    DEFAULT_COMMAND_CONFIG,
    DEFAULT_AGENT_CONFIG
)

# OAuth/SSO Authentication
from .oauth_handler import (
    OAuthHandler,
    create_oauth_callback
)

# Data Layer Factory
from .data_layer_factory import (
    DataLayerFactory,
    create_data_layer_decorator,
    register_qdrant_data_layer
)

# Thread Resume Handler
from .thread_resume_handler import (
    ThreadResumeHandler,
    create_resume_handler
)

# Utilities
from .utils import (
    get_env_with_fallback,
    setup_logging,
    load_instruction_file,
    format_session_id,
    extract_short_id,
    get_mode_emoji
)

# Session Management
from .session_manager import (
    SessionManager,
    query_sessions_by_user,
    query_all_sessions,
    query_session_by_id,
    aggregate_sessions
)

# Command Handlers
from .command_handlers import (
    CommandRouter,
    handle_debug_command,
    handle_list_sessions_command,
    handle_session_info_command,
    handle_mode_switch
)

# Session UI
from .session_ui import (
    SessionUI,
    display_session_browser,
    restore_session_by_id,
    find_and_restore_session
)

# Agent Factory
from .agent_factory import (
    AgentFactory,
    create_chat_client,
    create_agent,
    load_instructions
)

__all__ = [
    # Config
    "AgentMode",
    "SessionConfig", 
    "CommandConfig",
    "AgentConfig",
    "DEFAULT_SESSION_CONFIG",
    "DEFAULT_COMMAND_CONFIG",
    "DEFAULT_AGENT_CONFIG",
    
    # Utils
    "get_env_with_fallback",
    "setup_logging",
    "load_instruction_file",
    "format_session_id",
    "extract_short_id",
    "get_mode_emoji",
    
    # Session Management
    "SessionManager",
    "query_sessions_by_user",
    "query_all_sessions",
    "query_session_by_id",
    "aggregate_sessions",
    
    # Command Handlers
    "CommandRouter",
    "handle_debug_command",
    "handle_list_sessions_command",
    "handle_session_info_command",
    "handle_mode_switch",
    
    # Session UI
    "SessionUI",
    "display_session_browser",
    "restore_session_by_id",
    "find_and_restore_session",
    
    # Agent Factory
    "AgentFactory",
    "create_chat_client",
    "create_agent",
    "load_instructions",
    
    # OAuth/SSO (NEW in v1.1.0)
    "OAuthHandler",
    "create_oauth_callback",
    
    # Data Layer (NEW in v1.1.0)
    "DataLayerFactory",
    "create_data_layer_decorator",
    "register_qdrant_data_layer",
    
    # Thread Resume (NEW in v1.1.0)
    "ThreadResumeHandler",
    "create_resume_handler",
]

from .session_manager import (
    SessionManager,
    query_sessions_by_user,
    query_all_sessions,
    query_session_by_id,
    aggregate_sessions,
    format_session_id,
    extract_short_id,
)

from .command_handlers import (
    CommandRouter,
    handle_debug_command,
    handle_list_sessions_command,
    handle_session_info_command,
    handle_mode_switch,
)

from .session_ui import (
    display_session_browser,
    restore_session_by_id,
    find_and_restore_session,
)

from .config import (
    AgentConfig,
    SessionConfig,
    DEFAULT_SESSION_CONFIG,
)

from .utils import (
    get_env_with_fallback,
    setup_logging,
)

from .agent_factory import (
    AgentFactory,
    create_chat_client,
)

__version__ = "1.1.0"  # Added SSO/OAuth, Data Layer, and Thread Resume support
