#!/bin/bash
# Script to create a new agent from template

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if agent name provided
if [ -z "$1" ]; then
    print_error "Agent name required!"
    echo ""
    echo "Usage: $0 <agent_name> [emoji] [description]"
    echo ""
    echo "Examples:"
    echo "  $0 security_sentinel"
    echo "  $0 devops_helper 📦 'DevOps automation assistant'"
    echo "  $0 data_analyst 📊 'Data analysis and insights'"
    exit 1
fi

AGENT_NAME="$1"
AGENT_EMOJI="${2:-🤖}"
AGENT_DESCRIPTION="${3:-AI Assistant}"

# Validate agent name (lowercase, alphanumeric, underscores)
if ! [[ "$AGENT_NAME" =~ ^[a-z][a-z0-9_]*$ ]]; then
    print_error "Invalid agent name!"
    echo "  Agent name must:"
    echo "  - Start with a lowercase letter"
    echo "  - Contain only lowercase letters, numbers, and underscores"
    echo "  Example: security_sentinel, devops_helper"
    exit 1
fi

# Convert agent name to PascalCase for display
AGENT_CLASS_NAME=$(echo "$AGENT_NAME" | sed -r 's/(^|_)([a-z])/\U\2/g')

AGENT_DIR="$PROJECT_ROOT/agents/$AGENT_NAME"

# Check if agent already exists
if [ -d "$AGENT_DIR" ]; then
    print_error "Agent '$AGENT_NAME' already exists at $AGENT_DIR"
    exit 1
fi

echo ""
echo "🏛️  Pantheon - Agent Generator"
echo "=========================================="
echo ""
print_info "Creating new agent: $AGENT_NAME"
echo "  Display Name: $AGENT_CLASS_NAME"
echo "  Emoji: $AGENT_EMOJI"
echo "  Description: $AGENT_DESCRIPTION"
echo "  Location: agents/$AGENT_NAME/"
echo ""

# Create directory structure
print_info "Creating directory structure..."
mkdir -p "$AGENT_DIR"
mkdir -p "$AGENT_DIR/instructions"
mkdir -p "$AGENT_DIR/mcp_tools"
mkdir -p "$AGENT_DIR/templates"
mkdir -p "$PROJECT_ROOT/tests/unit/test_agents/test_$AGENT_NAME"

print_success "Directories created"

# Create __init__.py
print_info "Creating __init__.py..."
cat > "$AGENT_DIR/__init__.py" << EOF
"""
$AGENT_CLASS_NAME - $AGENT_DESCRIPTION
Part of the Pantheon multi-agent system
"""

__version__ = "1.0.0"
__agent_name__ = "$AGENT_CLASS_NAME"
__description__ = "$AGENT_DESCRIPTION"
EOF

print_success "__init__.py created"

# Create main.py
print_info "Creating main.py..."
cat > "$AGENT_DIR/main.py" << 'EOFMAIN'
"""
{AGENT_CLASS_NAME} - {AGENT_DESCRIPTION}
Part of the Pantheon multi-agent system
"""
import logging
import sys
from pathlib import Path
from typing import Optional

# Add project root to Python path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
    "default": AgentMode(
        name="Default Mode",
        file="instructions/default_instructions.txt",
        emoji="{AGENT_EMOJI}",
        description="{AGENT_DESCRIPTION}"
    ),
    # Add more modes as needed
}

# Create agent configuration
{AGENT_NAME_UPPER}_CONFIG = AgentConfig(
    agent_name="{AGENT_CLASS_NAME}",
    agent_modes=AGENT_MODES,
    default_mode="default",
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
    log_file="{AGENT_NAME}.log",
    temperature=0.2
)

# Initialize components
factory = AgentFactory({AGENT_NAME_UPPER}_CONFIG)
session_manager = SessionManager({AGENT_NAME_UPPER}_CONFIG.session_config)
command_router = CommandRouter({AGENT_NAME_UPPER}_CONFIG.command_config, session_manager)
session_ui = SessionUI({AGENT_NAME_UPPER}_CONFIG.session_config, session_manager)

# Initialize SSO/OAuth handler
oauth_handler = OAuthHandler()
oauth_handler.validate_env_vars()

# Initialize thread resume handler
resume_handler = ThreadResumeHandler(
    agent_modes=AGENT_MODES,
    agent_factory_func=factory.create_agent,
    default_mode={AGENT_NAME_UPPER}_CONFIG.default_mode,
    max_history_messages={AGENT_NAME_UPPER}_CONFIG.session_config.max_history_messages
)

# Setup logging
logger = setup_logging({AGENT_NAME_UPPER}_CONFIG.log_file, {AGENT_NAME_UPPER}_CONFIG.log_level)

{AGENT_NAME_UPPER}_INTRO = (
    "👋 Hi, I'm {AGENT_CLASS_NAME}! {AGENT_DESCRIPTION}. "
    "How can I help you today?"
)

# ============================================================================
# CHAINLIT LIFECYCLE HOOKS
# ============================================================================

@cl.on_chat_start
async def on_chat_start():
    """Initialize chat session"""
    user = cl.user_session.get("user")
    user_id = user.identifier if user else "default_user"
    
    cl.user_session.set("user_id", user_id)
    current_mode = {AGENT_NAME_UPPER}_CONFIG.default_mode
    cl.user_session.set("current_mode", current_mode)
    
    # Create vector memory
    vector_memory = create_vector_memory_manager(
        collection_name="{AGENT_NAME}_sessions",
        user_id=user_id
    )
    cl.user_session.set("vector_memory", vector_memory)
    
    # Create agent
    agent = await factory.create_agent(mode_name=current_mode)
    cl.user_session.set("agent", agent)
    
    # Display session browser
    mode_emojis = {name: mode.emoji for name, mode in AGENT_MODES.items()}
    await session_ui.display_browser(vector_memory, user_id, mode_emojis)
    
    # Welcome message
    await cl.Message(content={AGENT_NAME_UPPER}_INTRO).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages"""
    vector_memory = cl.user_session.get("vector_memory")
    agent = cl.user_session.get("agent")
    user_id = cl.user_session.get("user_id")
    session_id = cl.user_session.get("id")
    current_mode = cl.user_session.get("current_mode")
    
    # Route commands
    is_command = await command_router.route(
        message=message.content,
        vector_memory=vector_memory,
        user_id=user_id,
        available_modes=AGENT_MODES
    )
    
    if is_command:
        return
    
    # Store user message
    await vector_memory.store_message(
        session_id=session_id,
        user_id=user_id,
        message=message.content,
        role="user",
        agent_mode=current_mode
    )
    
    # Get agent response
    response_msg = cl.Message(content="")
    await response_msg.send()
    
    async for chunk in agent.invoke_stream(message.content):
        await response_msg.stream_token(chunk)
    
    await response_msg.update()
    
    # Store assistant response
    await vector_memory.store_message(
        session_id=session_id,
        user_id=user_id,
        message=response_msg.content,
        role="assistant",
        agent_mode=current_mode
    )


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    """Resume previous chat session"""
    await resume_handler.handle_resume(thread)


@cl.action_callback("restore_*")
async def on_restore_session(action: cl.Action):
    """Handle session restoration from browser"""
    session_id = action.value
    current_session_id = cl.user_session.get("id")
    vector_memory = cl.user_session.get("vector_memory")
    
    await session_ui.restore_by_id(vector_memory, session_id, current_session_id)
EOFMAIN

# Replace placeholders
sed -i.bak "s/{AGENT_CLASS_NAME}/$AGENT_CLASS_NAME/g" "$AGENT_DIR/main.py"
sed -i.bak "s/{AGENT_DESCRIPTION}/$AGENT_DESCRIPTION/g" "$AGENT_DIR/main.py"
sed -i.bak "s/{AGENT_EMOJI}/$AGENT_EMOJI/g" "$AGENT_DIR/main.py"
sed -i.bak "s/{AGENT_NAME}/$AGENT_NAME/g" "$AGENT_DIR/main.py"
sed -i.bak "s/{AGENT_NAME_UPPER}/$(echo $AGENT_NAME | tr '[:lower:]' '[:upper:]')/g" "$AGENT_DIR/main.py"
rm "$AGENT_DIR/main.py.bak"

print_success "main.py created"

# Create default instruction file
print_info "Creating instruction file..."
cat > "$AGENT_DIR/instructions/default_instructions.txt" << EOF
You are $AGENT_CLASS_NAME, $AGENT_DESCRIPTION.

Your role is to assist users with:
- [Add specific capabilities]
- [Add more capabilities]

Guidelines:
- Be helpful and professional
- Provide accurate information
- Ask clarifying questions when needed
- Format responses clearly

Example interactions:
[Add example conversations]
EOF

print_success "Instruction file created"

# Create README
print_info "Creating README.md..."
cat > "$AGENT_DIR/README.md" << EOF
# $AGENT_EMOJI $AGENT_CLASS_NAME

> $AGENT_DESCRIPTION

## Overview

[Add detailed description of the agent]

## Quick Start

\`\`\`bash
python launcher.py $AGENT_NAME
\`\`\`

## Features

- Feature 1
- Feature 2
- Feature 3

## Configuration

Required environment variables:
\`\`\`bash
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
\`\`\`

## Agent Modes

### Default Mode
[Describe default mode]

## Commands

- \`/sessions\` - View previous sessions
- \`/debug\` - Show debug information
- \`/session\` - Current session info

## Development

[Add development notes]

---

*Part of the Pantheon Multi-Agent System* 🏛️
EOF

print_success "README.md created"

# Create test file
print_info "Creating test file..."
cat > "$PROJECT_ROOT/tests/unit/test_agents/test_$AGENT_NAME/test_main.py" << EOF
"""
Tests for $AGENT_CLASS_NAME agent
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch


class Test${AGENT_CLASS_NAME}:
    """Test $AGENT_CLASS_NAME agent"""
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        # TODO: Add initialization test
        pass
    
    @pytest.mark.asyncio
    async def test_agent_response(self):
        """Test agent generates responses"""
        # TODO: Add response test
        pass
EOF

print_success "Test file created"

# Create startup script
print_info "Creating startup script..."
cat > "$PROJECT_ROOT/scripts/start_$AGENT_NAME.sh" << EOF
#!/bin/bash
# Quick start script for $AGENT_CLASS_NAME in Pantheon

echo "🏛️ Pantheon - Starting $AGENT_CLASS_NAME..."

# Get script directory and navigate to project root
SCRIPT_DIR="\$( cd "\$( dirname "\${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="\$( cd "\$SCRIPT_DIR/.." && pwd )"
cd "\$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Set PYTHONPATH to project root for imports
export PYTHONPATH="\$PROJECT_ROOT"

# Install dependencies
pip install -r requirements.txt -q

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "Please create .env from .env.example and configure your credentials."
    exit 1
fi

# Start Chainlit with $AGENT_CLASS_NAME (without -w flag to avoid reload loops)
echo "Starting $AGENT_CLASS_NAME on http://localhost:8000"
chainlit run agents/$AGENT_NAME/main.py
EOF

chmod +x "$PROJECT_ROOT/scripts/start_$AGENT_NAME.sh"
print_success "Startup script created"

# Create .gitkeep files
touch "$AGENT_DIR/mcp_tools/.gitkeep"
touch "$AGENT_DIR/templates/.gitkeep"

echo ""
print_success "Agent '$AGENT_NAME' created successfully!"
echo ""
echo "📁 Created files:"
echo "  ✓ agents/$AGENT_NAME/__init__.py"
echo "  ✓ agents/$AGENT_NAME/main.py"
echo "  ✓ agents/$AGENT_NAME/README.md"
echo "  ✓ agents/$AGENT_NAME/instructions/default_instructions.txt"
echo "  ✓ scripts/start_$AGENT_NAME.sh"
echo "  ✓ tests/unit/test_agents/test_$AGENT_NAME/test_main.py"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Update instruction file:"
echo "   Edit agents/$AGENT_NAME/instructions/default_instructions.txt"
echo ""
echo "2. Register agent in launcher:"
echo "   Edit launcher.py and add to AGENTS dictionary:"
echo "   \"$AGENT_NAME\": {"
echo "       \"name\": \"$AGENT_CLASS_NAME\","
echo "       \"description\": \"$AGENT_DESCRIPTION\","
echo "       \"emoji\": \"$AGENT_EMOJI\","
echo "       \"path\": \"agents/$AGENT_NAME/main.py\","
echo "       \"modes\": [\"default\"],"
echo "       \"default_mode\": \"default\","
echo "       \"port\": 8001"
echo "   }"
echo ""
echo "3. Test the agent:"
echo "   bash scripts/start_$AGENT_NAME.sh"
echo "   OR"
echo "   python launcher.py $AGENT_NAME"
echo ""
echo "4. Write tests:"
echo "   pytest tests/unit/test_agents/test_$AGENT_NAME/ -v"
echo ""
print_info "Happy coding! 🚀"
echo ""
