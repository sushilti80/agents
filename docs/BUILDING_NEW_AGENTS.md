# Building New Agents with Pantheon Framework

This guide shows you how to create new agents using the reusable `core` library in the Pantheon multi-agent system. You can either create a standalone agent or add modes to existing multi-mode agents like Daedalus.

## 📚 Table of Contents

1. [Quick Start](#quick-start)
2. [Approach 1: Create Standalone Agent](#approach-1-create-standalone-agent)
3. [Approach 2: Add Mode to Existing Agent](#approach-2-add-mode-to-existing-agent)
4. [Common Patterns](#common-patterns)
5. [Testing Your Agent](#testing-your-agent)

---

## 🚀 Quick Start

### Prerequisites

- ✅ `core/` library installed (renamed from agent_core)
- ✅ `shared/` utilities available (vector_memory, qdrant_data_layer)
- ✅ Azure OpenAI credentials configured
- ✅ Qdrant running (for conversation memory)

### What core Provides

```python
from core import (
    # Configuration
    AgentConfig, AgentMode, SessionConfig, CommandConfig,
    
    # Core Components
    AgentFactory,        # Create agents with different modes
    SessionManager,      # Manage conversation sessions
    CommandRouter,       # Handle /commands
    SessionUI,           # Display session browser
    
    # SSO/OAuth
    OAuthHandler,        # Microsoft Entra ID authentication
    DataLayerFactory,    # Qdrant data layer for thread history
    ThreadResumeHandler, # Resume conversations from sidebar
    
    # Monitoring
    QdrantMonitor,       # RAG performance metrics
    
    # Utilities
    setup_logging,       # Logging configuration
    get_env_with_fallback, # Environment variable helpers
)
```

---

## 📝 Approach 1: Create Standalone Agent

Create a new single-purpose agent from scratch.

### Step 1: Create Agent File

**File:** `agents/my_agent/main.py`

```python
"""
My Custom Agent - Description of what this agent does
Built using Pantheon core library for SSO, session management, and RAG
"""
import logging
from pathlib import Path
from typing import Optional

import chainlit as cl
from chainlit.types import ThreadDict
from dotenv import load_dotenv
from shared.vector_memory import create_vector_memory_manager

# Import from core library
from core import (
    AgentMode,
    AgentConfig,
    SessionConfig,
    CommandConfig,
    AgentFactory,
    SessionManager,
    CommandRouter,
    SessionUI,
    setup_logging,
    OAuthHandler,
    DataLayerFactory,
    ThreadResumeHandler,
    QdrantMonitor
)

load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

# Define agent mode (single mode agent)
AGENT_MODES = {
    "default": AgentMode(
        name="My Custom Agent",
        file="my_agent_instructions.txt",
        emoji="🤖",
        description="Custom agent for specific tasks"
    )
}

# Create agent configuration
MY_AGENT_CONFIG = AgentConfig(
    agent_name="MyAgent",
    agent_modes=AGENT_MODES,
    default_mode="default",
    session_config=SessionConfig(
        max_sessions_query=100,
        max_sessions_display=10,
        max_history_messages=100
    ),
    command_config=CommandConfig(
        debug=["/debug"],
        list_sessions=["/sessions", "/list"],
        session_info="/session",
        resume="/resume"
    ),
    instruction_base_dir=str(Path(__file__).parent / "instructions"),
    log_file="my_agent.log",
    temperature=0.2
)

# Initialize components
factory = AgentFactory(MY_AGENT_CONFIG)
session_manager = SessionManager(MY_AGENT_CONFIG.session_config)
command_router = CommandRouter(MY_AGENT_CONFIG.command_config, session_manager)
session_ui = SessionUI(MY_AGENT_CONFIG.session_config, session_manager)

# Initialize SSO/OAuth handler
oauth_handler = OAuthHandler()
oauth_handler.validate_env_vars()

# Initialize thread resume handler
resume_handler = ThreadResumeHandler(
    agent_modes=AGENT_MODES,
    agent_factory_func=factory.create_agent,
    default_mode=MY_AGENT_CONFIG.default_mode,
    max_history_messages=MY_AGENT_CONFIG.session_config.max_history_messages
)

# Setup logging
logger = setup_logging(MY_AGENT_CONFIG.log_file, MY_AGENT_CONFIG.log_level)

MY_AGENT_INTRO = (
    "👋 Hi, I'm MyAgent! I help with [describe what your agent does]. "
    "Ask me anything about [your domain]!"
)

# ============================================================================
# DATA LAYER REGISTRATION (for thread history sidebar)
# ============================================================================

@cl.data_layer
def get_data_layer():
    """Register Qdrant data layer for thread history sidebar."""
    return DataLayerFactory.create_qdrant_data_layer()

# ============================================================================
# SSO/OAUTH HANDLER
# ============================================================================

@cl.oauth_callback
def oauth_callback(provider_id: str, token: str, raw_user_info: dict, default_user: cl.User) -> Optional[cl.User]:
    """Handle OAuth callback - extracts user info from Microsoft Entra ID"""
    return oauth_handler.handle_callback(provider_id, token, raw_user_info, default_user)

# ============================================================================
# CHAT HANDLERS
# ============================================================================

@cl.on_settings_update
async def on_settings_update(settings):
    """Handle settings updates (session selection from sidebar)"""
    selected_session = settings.get("session_selector")
    
    if selected_session and selected_session != "current":
        logger.info(f"User selected session from settings: {selected_session}")
        try:
            current_session_id = cl.user_session.get("session_id")
            vector_memory = cl.user_session.get("vector_memory")
            await session_ui.restore_by_id(
                vector_memory, 
                selected_session, 
                current_session_id,
                agent_factory_func=factory.create_agent
            )
        except Exception as e:
            logger.error(f"Failed to restore session from settings: {e}")
            await cl.Message(content=f"❌ Failed to restore session: {str(e)}").send()


@cl.action_callback("resume_*")
async def on_session_restore_action(action: cl.Action):
    """Handle session restore action when user clicks a session button"""
    session_id = action.value
    current_session_id = cl.user_session.get("session_id")
    vector_memory = cl.user_session.get("vector_memory")
    
    logger.info(f"🔘 User clicked to restore session: {session_id}")
    await session_ui.restore_by_id(
        vector_memory, 
        session_id, 
        current_session_id,
        agent_factory_func=factory.create_agent
    )


@cl.on_chat_start
async def start():
    """Initialize the agent for new conversations"""
    try:
        logger.info("Starting new chat session")
        
        # Log OAuth status
        oauth_handler.log_oauth_status()
        
        # Set default mode
        mode = MY_AGENT_CONFIG.default_mode
        cl.user_session.set("agent_mode", mode)
        
        # Initialize Vector Memory
        vector_memory = None
        try:
            vector_memory = create_vector_memory_manager()
            await vector_memory.ensure_collection()
            cl.user_session.set("vector_memory", vector_memory)
            logger.info("✅ Vector memory initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Vector memory unavailable: {e}")
        
        # Set user and session IDs
        resume_session_id = cl.user_session.get("chat_profile")
        user_id = cl.user_session.get("id", "anonymous")
        
        if resume_session_id:
            session_id = resume_session_id
            logger.info(f"📂 Resuming session: {session_id}")
        else:
            chainlit_session_id = cl.context.session.id
            session_id = f"session_{chainlit_session_id}"
            logger.info(f"🆕 Creating new session: {session_id}")
        
        cl.user_session.set("user_id", user_id)
        cl.user_session.set("session_id", session_id)
        
        # Display session browser using agent_core
        if vector_memory:
            mode_emojis = {name: m.emoji for name, m in AGENT_MODES.items()}
            await session_ui.display_browser(vector_memory, user_id, mode_emojis)
        
        # Create agent using factory
        agent = await factory.create_agent(mode_name=mode)
        if not agent:
            await cl.Message(
                content="⚠️ Azure OpenAI credentials are missing or invalid.\n\n"
                        "Please set the required environment variables in your .env file."
            ).send()
            return

        thread = agent.get_new_thread()
        cl.user_session.set("agent", agent)
        cl.user_session.set("thread", thread)

        # Send welcome message
        mode_info = AGENT_MODES[mode]
        welcome_msg = (
            f"{mode_info.emoji} **{mode_info.name} is Ready!**\n\n"
            f"{MY_AGENT_INTRO}\n\n"
            f"How can I assist you today?"
        )
        
        await cl.Message(content=welcome_msg).send()
        logger.info("✅ Chat session initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing agent: {e}", exc_info=True)
        await cl.Message(
            content=f"❌ **Error initializing agent:** {str(e)}\n\n"
                    "Please check your configuration."
        ).send()


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    """Handle thread resumption when user clicks on sidebar thread"""
    await resume_handler.handle_resume(thread)


@cl.on_message
async def handle_message(message: cl.Message):
    """Handle incoming user messages with command routing and vector memory"""
    try:
        content = message.content.strip()
        
        # Get session variables
        vector_memory = cl.user_session.get("vector_memory")
        user_id = cl.user_session.get("user_id")
        
        # Route commands using agent_core CommandRouter
        is_command = await command_router.route(
            message=content,
            vector_memory=vector_memory,
            user_id=user_id,
            available_modes=AGENT_MODES
        )
        
        if is_command:
            return
        
        # Normal message processing
        agent = cl.user_session.get("agent")
        thread = cl.user_session.get("thread")
        session_id = cl.user_session.get("session_id")
        agent_mode = cl.user_session.get("agent_mode")
        
        if not agent or not thread:
            await cl.Message(content="❌ Agent not initialized.").send()
            return
        
        logger.info(f"Processing user query: {message.content}")
        
        # Store user message in vector memory
        if vector_memory:
            try:
                qdrant_monitor = QdrantMonitor(model="gpt-4")
                qdrant_monitor.log_storage(user_id, message.content, "user")
                
                await vector_memory.store_message(
                    user_id=user_id,
                    session_id=session_id,
                    message=message.content,
                    role="user",
                    agent_mode=agent_mode
                )
                logger.debug("✅ User message stored")
            except Exception as e:
                logger.warning(f"⚠️ Failed to store message: {e}")
        
        # Retrieve relevant context (RAG)
        context_prefix = ""
        if vector_memory:
            try:
                qdrant_monitor = QdrantMonitor(model="gpt-4")
                
                # Search for semantically similar past conversations
                relevant_context = await vector_memory.search_context(
                    user_id=user_id,
                    query=message.content,
                    top_k=5,
                    session_id=session_id
                )
                
                # Get full history for metrics
                full_history = await vector_memory.get_session_history(
                    user_id=user_id,
                    session_id=session_id,
                    limit=100
                )
                
                # Log RAG metrics
                qdrant_monitor.log_retrieval(
                    query=message.content,
                    context=relevant_context,
                    full_history_size=len(full_history),
                    show_details=True
                )
                
                if relevant_context:
                    context_prefix = vector_memory.format_context_for_prompt(relevant_context)
                    logger.info(f"✅ Retrieved {len(relevant_context)} context items")
            except Exception as e:
                logger.warning(f"⚠️ Failed to retrieve context: {e}")
        
        # Run agent with augmented query
        async with cl.Step(name="Thinking...") as step:
            augmented_query = f"{context_prefix}{message.content}" if context_prefix else message.content
            result = await agent.run(augmented_query, thread=thread)
            step.output = "Processing complete"
        
        # Store assistant response
        if vector_memory:
            try:
                qdrant_monitor = QdrantMonitor(model="gpt-4")
                qdrant_monitor.log_storage(user_id, result.text, "assistant")
                
                await vector_memory.store_message(
                    user_id=user_id,
                    session_id=session_id,
                    message=result.text,
                    role="assistant",
                    agent_mode=agent_mode
                )
                logger.debug("✅ Assistant response stored")
            except Exception as e:
                logger.warning(f"⚠️ Failed to store response: {e}")
        
        await cl.Message(content=result.text).send()
        logger.info("Response sent successfully")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        await cl.Message(content=f"❌ **Error:** {str(e)}").send()
```

### Step 2: Create Instruction File

**File:** `agents/my_agent/instructions/default_instructions.txt`

```
You are MyAgent, a helpful AI assistant specialized in [your domain].

Your capabilities:
- [Capability 1]
- [Capability 2]
- [Capability 3]

Guidelines:
- Be helpful and accurate
- Provide code examples when relevant
- Ask clarifying questions
- Admit when you don't know something

Always maintain a professional and friendly tone.
```

### Step 3: Run Your Agent

Using the Pantheon launcher:
```bash
python launcher.py launch my_agent
```

Or directly with Chainlit:
```bash
chainlit run agents/my_agent/main.py
```

Or using the convenience script:
```bash
bash scripts/start_my_agent.sh
```

---

## 🔄 Approach 2: Add Mode to Existing Agent

Add a new mode to an existing multi-mode agent like Daedalus.

### Step 1: Create Instruction File

**File:** `agents/daedalus/instructions/kubernetes_architect_instructions.txt`

```
You are a Kubernetes Architecture Specialist.

Your expertise:
- Kubernetes cluster design and architecture
- Container orchestration best practices
- Helm charts and package management
- Service mesh (Istio, Linkerd)
- GitOps and CI/CD for K8s

Guidelines:
- Recommend cloud-native patterns
- Focus on scalability and reliability
- Provide YAML examples
- Consider security best practices
```

### Step 2: Update Agent Configuration

**Edit:** `agents/daedalus/main.py`

```python
# Define agent modes
AGENT_MODES = {
    "platform": AgentMode(
        name="Platform Architect",
        file="platform_architect_instructions.txt",
        emoji="🏗️",
        description="Azure Platform Architect with Aya Service Catalog"
    ),
    "cloud": AgentMode(
        name="MS Cloud Architect",
        file="ms_cloud_architect_instructions.txt",
        emoji="☁️",
        description="Microsoft Cloud Solutions across Azure, M365, Power Platform"
    ),
    # ✨ NEW MODE
    "kubernetes": AgentMode(
        name="Kubernetes Architect",
        file="kubernetes_architect_instructions.txt",
        emoji="⎈",
        description="Kubernetes and cloud-native architecture specialist"
    )
}
```

### Step 3: Add Mode Switch Handler

```python
# In handle_message function, add new mode switch command
@cl.on_message
async def handle_message(message: cl.Message):
    try:
        content = message.content.strip()
        
        # ... existing code ...
        
        # Handle mode switch commands
        if content in ["/platform", "/cloud", "/kubernetes"]:  # ✨ Add new mode
            mode = content[1:]  # Remove leading /
            await handle_mode_switch(mode)
            return
        
        # ... rest of code ...
```

### Step 4: Test New Mode

Using the Pantheon launcher:
```bash
python launcher.py launch daedalus --mode kubernetes

# In chat:
/kubernetes
> ✅ Switched to **Kubernetes Architect** mode!
> ⎈ Kubernetes and cloud-native architecture specialist

# Verify mode
/session
> **Agent Mode:** ⎈ Kubernetes Architect
```

---

## 🔧 Common Patterns

### Pattern 1: Custom Command Handler

```python
async def handle_custom_command(param: str):
    """Handle custom /command"""
    # Your logic here
    await cl.Message(content=f"Executed with param: {param}").send()

# In handle_message:
if content.startswith("/mycmd "):
    param = content.replace("/mycmd ", "").strip()
    await handle_custom_command(param)
    return
```

### Pattern 2: Multiple Instruction Files per Mode

```python
AGENT_MODES = {
    "expert": AgentMode(
        name="Domain Expert",
        file="expert_base_instructions.txt",
        emoji="🎓",
        description="Expert with additional context",
        # Store additional files in metadata if needed
        metadata={
            "additional_instructions": [
                "expert_advanced.txt",
                "expert_examples.txt"
            ]
        }
    )
}

# Load and combine instructions
def load_combined_instructions(mode: str) -> str:
    mode_info = AGENT_MODES[mode]
    base = Path(mode_info.file).read_text()
    
    additional = mode_info.metadata.get("additional_instructions", [])
    for file in additional:
        base += "\n\n" + Path(file).read_text()
    
    return base
```

### Pattern 3: Conditional Features by Mode

```python
@cl.on_message
async def handle_message(message: cl.Message):
    agent_mode = cl.user_session.get("agent_mode")
    
    # Enable special features only for certain modes
    if agent_mode == "expert":
        # Show advanced options
        await cl.Message(
            content="💡 Tip: Use /analyze for deep analysis"
        ).send()
    
    # Normal processing
    # ...
```

### Pattern 4: Mode-Specific RAG Context

```python
# Retrieve context with mode-specific filtering
if vector_memory:
    relevant_context = await vector_memory.search_context(
        user_id=user_id,
        query=message.content,
        top_k=5,
        session_id=session_id  # Already filters by session
    )
    
    # Further filter by current mode if needed
    if agent_mode == "platform":
        # Only include platform-mode context
        relevant_context = [
            ctx for ctx in relevant_context 
            if ctx.get("agent_mode") == "platform"
        ]
```

---

## 🧪 Testing Your Agent

### 1. Basic Functionality Test

```bash
# Start agent
chainlit run my_agent.py

# Test conversation
> Hello
< Welcome message

# Test commands
> /session
< Shows session info

> /sessions
< Lists sessions
```

### 2. Mode Switching Test (Multi-mode agents)

```bash
> /platform
< Switched to Platform Architect mode

> /session
< Agent Mode: 🏗️ Platform Architect

> /kubernetes
< Switched to Kubernetes Architect mode

> /session
< Agent Mode: ⎈ Kubernetes Architect
```

### 3. Session Restore Test

```bash
# 1. Create session and chat
> Hello, I need help with Azure
< ... response ...

# 2. Note session ID
> /session
< Session ID: session_abc123...

# 3. Restart app
# Ctrl+C, then: chainlit run my_agent.py

# 4. Resume session
> /resume session_abc123
< ✅ Session restored in platform mode
< (Shows previous messages)
```

### 4. RAG Context Test

```bash
# 1. Chat about topic
> What is Azure Kubernetes Service?
< AKS is...

# 2. Ask related question (should use context)
> What are the pricing tiers?
< (Should reference AKS from previous context)

# Check logs for RAG metrics
tail -f my_agent.log | grep "Context Quality"
```

### 5. Multi-User Test (SSO)

```bash
# User 1 session
# Login as user1@company.com
> Create session...

# User 2 session  
# Login as user2@company.com
> Create session...

# Verify isolation
> /sessions
< (Only shows user2's sessions, not user1's)
```

---

## 📊 Monitoring & Debugging

### Check Logs

```bash
# Real-time monitoring
tail -f my_agent.log

# Search for errors
grep ERROR my_agent.log

# Monitor mode switches
grep "Switching from" my_agent.log

# Monitor RAG metrics
grep "Context Quality" my_agent.log
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run agent
chainlit run my_agent.py

# Use debug command in chat
> /debug
< Shows session debug info
```

### Performance Monitoring

```python
# Add to your agent
from agent_core import QdrantMonitor

qdrant_monitor = QdrantMonitor(model="gpt-4")

# Monitor retrieval performance
qdrant_monitor.log_retrieval(
    query=message.content,
    context=relevant_context,
    full_history_size=len(full_history),
    show_details=True  # Detailed metrics
)
```

---

## ✅ Checklist for New Agent

### Standalone Agent
- [ ] Create `my_agent.py` with all handlers
- [ ] Create `my_agent_instructions.txt`
- [ ] Configure `.env` with Azure credentials
- [ ] Test basic conversation
- [ ] Test session restore
- [ ] Test RAG context retrieval
- [ ] Test SSO (if enabled)
- [ ] Monitor logs for errors

### Adding Mode to Existing Agent
- [ ] Create `new_mode_instructions.txt`
- [ ] Add mode to `AGENT_MODES` dictionary
- [ ] Add mode switch command (`/newmode`)
- [ ] Update mode switch handler
- [ ] Test mode switching
- [ ] Test session restore with new mode
- [ ] Verify mode persistence across restarts
- [ ] Update documentation

---

## 📚 Reference

### Environment Variables

```bash
# Azure OpenAI (Required)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small

# Qdrant (Optional - for conversation memory)
QDRANT_HOST=localhost
QDRANT_PORT=6333

# OAuth/SSO (Optional)
OAUTH_AZURE_AD_CLIENT_ID=your-client-id
OAUTH_AZURE_AD_CLIENT_SECRET=your-client-secret
OAUTH_AZURE_AD_TENANT_ID=your-tenant-id

# Logging
LOG_LEVEL=INFO
```

### File Structure

```
pantheon/
├── core/                        # Reusable library (formerly agent_core)
├── shared/                      # Shared utilities
│   ├── vector_memory.py
│   └── qdrant_data_layer.py
├── agents/
│   └── my_agent/               # Your new agent
│       ├── main.py
│       ├── instructions/
│       │   └── default_instructions.txt
│       └── README.md
├── scripts/
│   └── start_my_agent.sh       # Convenience launcher
├── launcher.py                  # Multi-agent launcher
└── .env                         # Configuration
```

---

**Created:** 2025-11-01  
**Updated:** 2025-11-03 (Pantheon restructure)  
**Version:** 2.0.0  
**Compatible with:** Pantheon core v1.1.0+
