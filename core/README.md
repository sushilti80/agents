# Agent Core Library

A reusable library for building multi-agent systems with Chainlit, Qdrant vector memory, and Azure OpenAI.

## Overview

`agent_core` provides modular components for:
- **Session Management**: Query, aggregate, and restore conversation sessions from Qdrant
- **Command Routing**: Handle agent commands like `/debug`, `/sessions`, `/resume`
- **Session UI**: Display session browsers and restoration interfaces in Chainlit
- **Agent Factory**: Create and configure ChatAgent instances with MCP tools
- **Configuration**: Dataclasses for agent behavior, session limits, and command mappings

## Installation

The library is designed to be used within the semantic-kernel workspace:

```python
from agent_core import (
    AgentFactory,
    SessionManager,
    CommandRouter,
    SessionUI,
    AgentConfig,
    DEFAULT_AGENT_CONFIG
)
```

## Quick Start

### 1. Create an Agent

```python
from agent_core import AgentFactory, DEFAULT_AGENT_CONFIG

# Use default configuration
factory = AgentFactory(DEFAULT_AGENT_CONFIG)
agent = await factory.create_agent(mode_name="azure")

# Or customize configuration
from agent_core import AgentConfig, AgentMode

custom_config = AgentConfig(
    agent_name="my-agent",
    agent_modes={
        "azure": AgentMode(
            name="Azure Architecture",
            file="azure_mode.txt",
            emoji="☁️",
            description="Azure architecture assistance"
        )
    },
    default_mode="azure",
    temperature=0.3
)

factory = AgentFactory(custom_config)
agent = await factory.create_agent()
```

### 2. Manage Sessions

```python
from agent_core import SessionManager

manager = SessionManager()

# Query user's sessions
points, _ = await manager.query_by_user(vector_memory, user_id)

# Aggregate into summaries
sessions = manager.aggregate_sessions(points)

# Query specific session
session_points, _ = await manager.query_by_id(vector_memory, "session_abc123")
```

### 3. Display Session Browser

```python
from agent_core import SessionUI

ui = SessionUI()

# Display clickable session browser
await ui.display_browser(vector_memory, user_id, mode_emojis)

# Restore a session by ID
await ui.restore_by_id(vector_memory, "session_abc123", current_session_id)
```

### 4. Route Commands

```python
from agent_core import CommandRouter

router = CommandRouter()

# Route user message to appropriate handler
is_command = await router.route(
    message=user_message,
    vector_memory=vector_memory,
    user_id=user_id,
    available_modes=agent_modes
)

if not is_command:
    # Process as normal message
    response = await agent.chat(user_message)
```

## Architecture

```
agent_core/
├── __init__.py          # Public API exports
├── config.py            # Configuration dataclasses
├── utils.py             # Utility functions
├── session_manager.py   # Session queries and aggregation
├── command_handlers.py  # Command routing and handlers
├── session_ui.py        # Chainlit UI components
└── agent_factory.py     # Agent creation and setup
```

## Configuration

### AgentConfig

Main configuration for agent behavior:

```python
@dataclass
class AgentConfig:
    agent_name: str = "daedalus"
    agent_modes: Dict[str, AgentMode] = field(default_factory=dict)
    default_mode: str = "azure"
    session_config: SessionConfig = field(default_factory=lambda: DEFAULT_SESSION_CONFIG)
    command_config: CommandConfig = field(default_factory=lambda: DEFAULT_COMMAND_CONFIG)
    temperature: float = 0.2
    # Azure OpenAI environment variables
    azure_openai_api_key: List[str] = field(default_factory=list)
    azure_openai_endpoint: List[str] = field(default_factory=list)
    # ... more config options
```

### SessionConfig

Session management limits:

```python
@dataclass
class SessionConfig:
    max_sessions_query: int = 100       # Max sessions to query from Qdrant
    max_sessions_display: int = 10      # Max sessions in browser UI
    max_history_messages: int = 100     # Max messages to restore
    session_id_prefix: str = "session_"
    short_id_length: int = 8
```

### CommandConfig

Command mappings:

```python
@dataclass
class CommandConfig:
    debug: List[str] = field(default_factory=lambda: ["/debug"])
    list_sessions: List[str] = field(default_factory=lambda: ["/sessions"])
    session_info: str = "/session"
    resume: str = "/resume"
```

## Building a New Agent

Here's a complete example of building a new agent using `agent_core`:

```python
import chainlit as cl
from agent_core import (
    AgentFactory,
    SessionManager,
    CommandRouter,
    SessionUI,
    AgentConfig,
    AgentMode
)
from vector_memory import VectorMemoryManager

# Define agent configuration
config = AgentConfig(
    agent_name="my-sre-agent",
    agent_modes={
        "kubernetes": AgentMode(
            name="Kubernetes",
            file="k8s_instructions.txt",
            emoji="☸️",
            description="Kubernetes troubleshooting"
        ),
        "monitoring": AgentMode(
            name="Monitoring",
            file="monitoring_instructions.txt",
            emoji="📊",
            description="Monitoring and alerting"
        )
    },
    default_mode="kubernetes"
)

# Initialize components
factory = AgentFactory(config)
session_manager = SessionManager(config.session_config)
command_router = CommandRouter(config.command_config, session_manager)
session_ui = SessionUI(config.session_config, session_manager)

@cl.on_chat_start
async def on_chat_start():
    # Initialize vector memory
    vector_memory = VectorMemoryManager(
        collection_name="my_sre_agent_sessions",
        qdrant_host="localhost",
        qdrant_port=6333
    )
    cl.user_session.set("vector_memory", vector_memory)
    
    # Set user ID (customize based on your auth strategy)
    user_id = "default_user"
    cl.user_session.set("user_id", user_id)
    
    # Create agent
    agent = await factory.create_agent(mode_name="kubernetes")
    cl.user_session.set("agent", agent)
    cl.user_session.set("current_mode", "kubernetes")
    
    # Display session browser
    mode_emojis = {name: mode.emoji for name, mode in config.agent_modes.items()}
    await session_ui.display_browser(vector_memory, user_id, mode_emojis)
    
    await cl.Message(content="👋 SRE Agent ready! Type /help for commands.").send()

@cl.on_message
async def on_message(message: cl.Message):
    vector_memory = cl.user_session.get("vector_memory")
    agent = cl.user_session.get("agent")
    user_id = cl.user_session.get("user_id")
    
    # Route commands
    is_command = await command_router.route(
        message=message.content,
        vector_memory=vector_memory,
        user_id=user_id,
        available_modes=config.agent_modes
    )
    
    if is_command:
        return
    
    # Store user message in vector memory
    await vector_memory.store_message(
        session_id=cl.user_session.get("id"),
        user_id=user_id,
        message=message.content,
        role="user",
        agent_mode=cl.user_session.get("current_mode")
    )
    
    # Get agent response
    response = await agent.chat(message.content)
    
    # Store assistant response
    await vector_memory.store_message(
        session_id=cl.user_session.get("id"),
        user_id=user_id,
        message=response,
        role="assistant",
        agent_mode=cl.user_session.get("current_mode")
    )
    
    await cl.Message(content=response).send()

@cl.action_callback("restore_*")
async def on_restore_session(action: cl.Action):
    session_id = action.value
    current_session_id = cl.user_session.get("id")
    vector_memory = cl.user_session.get("vector_memory")
    
    await session_ui.restore_by_id(vector_memory, session_id, current_session_id)
```

## API Reference

### Classes

#### `SessionManager`
- `query_by_user(vector_memory, user_id, limit)` - Query sessions by user
- `query_all(vector_memory, limit)` - Query all sessions
- `query_by_id(vector_memory, session_id)` - Query specific session
- `aggregate_sessions(points)` - Aggregate points into session summaries

#### `CommandRouter`
- `route(message, vector_memory, user_id, available_modes)` - Route message to handler
- `handle_debug(vector_memory, user_id)` - Handle /debug command
- `handle_list_sessions(vector_memory, user_id)` - Handle /sessions command
- `handle_session_info()` - Handle /session command
- `handle_mode_switch(mode_name, mode)` - Handle mode switch

#### `SessionUI`
- `display_browser(vector_memory, user_id, mode_emojis)` - Display session browser
- `restore_by_id(vector_memory, session_id, current_session_id)` - Restore session
- `find_and_restore(vector_memory, user_id, session_hint, current_session_id)` - Find and restore

#### `AgentFactory`
- `create_chat_client()` - Create Azure OpenAI client
- `create_agent(mode_name, custom_instructions)` - Create configured agent
- `load_mode_instructions(mode, base_dir)` - Load instruction file
- `setup_mcp_tools()` - Setup MCP tools

### Utility Functions

- `get_env_with_fallback(primary, fallbacks)` - Get environment variable with fallbacks
- `setup_logging(log_file, log_level)` - Configure logging
- `load_instruction_file(file_path, base_dir)` - Load instruction text
- `format_session_id(session_id, prefix)` - Ensure session ID prefix
- `extract_short_id(session_id, length)` - Get short readable ID
- `get_mode_emoji(mode, mode_emojis)` - Get emoji for mode

## Environment Variables

Required for Azure OpenAI:
- `AZURE_OPENAI_API_KEY` - Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint URL
- `AZURE_OPENAI_DEPLOYMENT` - Chat deployment name

Optional:
- `AZURE_OPENAI_API_VERSION` - API version (default: 2024-02-15-preview)
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` - Embedding deployment name

## Dependencies

- `chainlit` - UI framework
- `qdrant-client` - Vector database
- `agent_framework` - Base agent classes
- `vector_memory` - Vector memory manager

## License

Part of the semantic-kernel workspace.
