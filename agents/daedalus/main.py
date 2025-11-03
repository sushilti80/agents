"""
Daedalus - Azure Architecture Assistant with Web Interface
Refactored to use agent_core library for reusability
Now with SSO support!
"""
import logging
from pathlib import Path
from typing import Optional

import chainlit as cl
from chainlit.types import ThreadDict
from dotenv import load_dotenv
from shared.vector_memory import create_vector_memory_manager

# Import from core library (renamed from agent_core)
from core import (
    AgentMode,
    AgentConfig,
    SessionConfig,
    CommandConfig,
    AgentFactory,
    SessionManager,
    CommandRouter,
    SessionUI,
    setup_logging
)

# Import SSO/OAuth components from core
from core.oauth_handler import OAuthHandler
from core.data_layer_factory import DataLayerFactory
from core.thread_resume_handler import ThreadResumeHandler
from core.qdrant_monitor import QdrantMonitor

load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

# Define agent modes
AGENT_MODES = {
    "platform": AgentMode(
        name="Platform Architect",
        file="instructions/platform_architect_instructions.txt",
        emoji="🏗️",
        description="Azure Platform Architect with Aya Service Catalog"
    ),
    "cloud": AgentMode(
        name="MS Cloud Architect",
        file="instructions/ms_cloud_architect_instructions.txt",
        emoji="☁️",
        description="Microsoft Cloud Solutions across Azure, M365, Power Platform"
    )
}

# Create agent configuration
DAEDALUS_CONFIG = AgentConfig(
    agent_name="Daedalus",
    agent_modes=AGENT_MODES,
    default_mode="platform",
    session_config=SessionConfig(
        max_sessions_query=100,
        max_sessions_display=10,
        max_history_messages=100
    ),
    command_config=CommandConfig(
        debug=["/debug", "/debug-sessions"],
        list_sessions=["/sessions", "/list"],
        session_info="/session",
        resume="/resume"
    ),
    instruction_base_dir=str(Path(__file__).parent),
    log_file="daedalus.log",
    temperature=0.2
)

# Initialize components
factory = AgentFactory(DAEDALUS_CONFIG)
session_manager = SessionManager(DAEDALUS_CONFIG.session_config)
command_router = CommandRouter(DAEDALUS_CONFIG.command_config, session_manager)
session_ui = SessionUI(DAEDALUS_CONFIG.session_config, session_manager)

# Initialize SSO/OAuth handler
oauth_handler = OAuthHandler()  # Uses default Azure AD providers
oauth_handler.validate_env_vars()  # Check OAuth configuration on startup

# Initialize thread resume handler
resume_handler = ThreadResumeHandler(
    agent_modes=AGENT_MODES,
    agent_factory_func=factory.create_agent,  # Use factory's create_agent method
    default_mode=DAEDALUS_CONFIG.default_mode,
    max_history_messages=DAEDALUS_CONFIG.session_config.max_history_messages
)

# Setup logging
logger = setup_logging(DAEDALUS_CONFIG.log_file, DAEDALUS_CONFIG.log_level)

DAEDALUS_INTRO = (
    "👋 Hi, I'm Daedalus! Your friendly (and slightly over-caffeinated) Azure architecture assistant. "
    "I help you design your initial cloud infrastructure, avoid rookie mistakes, and occasionally drop a dad joke. "
    "Ask me anything about Azure, cloud best practices, or how to avoid deploying your database to /dev/null! "
    "(And yes, it's pronounced 'DAY-duh-lus'—not 'Duh-DALE-us', 'Duh-DAH-loose', or 'That Greek guy with the wings.') "
    "Just a reminder: all my assistance is strictly within the self-service catalog. No forbidden labyrinths, no wax wings, just approved Azure services!"
)


# ============================================================================
# DATA LAYER REGISTRATION (for thread history sidebar)
# ============================================================================

@cl.data_layer
def get_data_layer():
    """
    Register Qdrant data layer for thread history sidebar.
    This enables the left sidebar showing conversation threads.
    """
    return DataLayerFactory.create_qdrant_data_layer()


# ============================================================================
# MODE SWITCH HANDLER (Custom to Daedalus)
# ============================================================================

async def handle_mode_switch(new_mode: str):
    """Handle mode switch command (/platform or /cloud) - Daedalus specific"""
    current_mode = cl.user_session.get("agent_mode")
    
    if new_mode == current_mode:
        mode_info = AGENT_MODES[new_mode]
        await cl.Message(
            content=f"ℹ️ Already in **{mode_info.name}** mode."
        ).send()
        return
    
    logger.info(f"Switching from {current_mode} to {new_mode} mode")
    
    # Create new agent using factory
    agent = await factory.create_agent(mode_name=new_mode)
    if not agent:
        await cl.Message(
            content="❌ Failed to switch mode. Please check Azure OpenAI credentials."
        ).send()
        return
    
    # Create new thread
    thread = agent.get_new_thread()
    
    # Update session
    cl.user_session.set("agent", agent)
    cl.user_session.set("thread", thread)
    cl.user_session.set("agent_mode", new_mode)
    
    mode_info = AGENT_MODES[new_mode]
    mode_note = "I use the FULL Azure service portfolio (not limited to any catalog). I can recommend ANY Azure service!" if new_mode == "cloud" else "I design using ONLY Aya Service Catalog services."
    
    await cl.Message(
        content=f"✅ Switched to **{mode_info.name}** mode!\n\n"
                f"{mode_info.emoji} {mode_info.description}\n\n"
                f"**Key Difference**: {mode_note}\n\n"
                f"New conversation started. How can I help?"
    ).send()
    
    logger.info(f"✅ Successfully switched to {new_mode} mode")


# ============================================================================
# CHAINLIT EVENT HANDLERS
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


# ============================================================================
# SSO/OAUTH HANDLER
# ============================================================================

@cl.oauth_callback
async def oauth_callback(provider_id: str, token: str, raw_user_info: dict, default_user: cl.User) -> Optional[cl.User]:
    """Handle OAuth callback - extracts user info from Microsoft Entra ID"""
    return await oauth_handler.handle_callback(provider_id, token, raw_user_info, default_user)


# ============================================================================
# CHAT HANDLERS
# ============================================================================

@cl.on_chat_start
async def start():
    """Initialize the agent for new conversations with vector memory and SSO"""
    try:
        logger.info("Starting new chat session")
        
        # Log OAuth status
        oauth_handler.log_oauth_status()
        
        # Set default mode
        mode = DAEDALUS_CONFIG.default_mode
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

        # Build welcome message
        mode_info = AGENT_MODES[mode]
        mode_note = "I design using ONLY Aya Service Catalog services." if mode == "platform" else "I use the FULL Azure service portfolio!"
         
        welcome_msg = (
            f"{mode_info.emoji} **{mode_info.name} is Ready!**\n\n"
            f"I'm {mode_info.description}.\n\n"
            f"**Note**: {mode_note}\n\n"
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
        
        # Handle mode switch commands (Daedalus specific)
        if content in ["/platform", "/cloud"]:
            mode = content[1:]  # Remove leading /
            await handle_mode_switch(mode)
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
                # Initialize monitor for storage logging
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
                # Initialize Qdrant monitor for detailed metrics
                qdrant_monitor = QdrantMonitor(model="gpt-4")
                
                # Search for semantically similar past conversations
                # IMPORTANT: Filter by session_id to keep context within current conversation
                relevant_context = await vector_memory.search_context(
                    user_id=user_id,
                    query=message.content,
                    top_k=5,  # Increased from 3 for better context coverage (filtered by score threshold)
                    session_id=session_id  # ✅ Filter by current session only
                )
                
                # Get full history size for token savings calculation
                full_history = await vector_memory.get_session_history(
                    user_id=user_id,
                    session_id=session_id,
                    limit=100
                )
                
                # Log detailed RAG metrics
                qdrant_monitor.log_retrieval(
                    query=message.content,
                    context=relevant_context,
                    full_history_size=len(full_history),
                    show_details=True  # Set to False to reduce log verbosity
                )
                
                # Log context quality metrics
                if relevant_context:
                    avg_score = sum(c.get('score', 0) for c in relevant_context) / len(relevant_context)
                    min_score = min(c.get('score', 0) for c in relevant_context)
                    max_score = max(c.get('score', 0) for c in relevant_context)
                    
                    logger.info(f"""
🎯 Context Quality Metrics:
   Session: {session_id[:8]}...
   Retrieved: {len(relevant_context)} messages (from {len(full_history)} total)
   Relevance Scores: Avg={avg_score:.3f}, Min={min_score:.3f}, Max={max_score:.3f}
   ✅ All results are from current session only
""")
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
                # Log assistant response storage
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
