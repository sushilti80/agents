# Pantheon Agents

This directory contains all agent implementations in the Pantheon multi-agent system.

## 🏛️ Available Agents

### 🏗️ Daedalus - Azure Architecture Assistant
**Status:** Active  
**Location:** `agents/daedalus/`  
**Modes:** Platform Architect, MS Cloud Architect  
**Description:** Azure cloud architecture guidance and best practices

**Quick Start:**
```bash
# From project root
python launcher.py daedalus

# Or use the dedicated script
./scripts/start_daedalus.sh
```

---

## 📁 Agent Directory Structure

Each agent follows this standard structure:

```
agents/
└── <agent_name>/
    ├── __init__.py              # Agent package initialization
    ├── main.py                  # Main agent entry point
    ├── config.py                # Agent-specific configuration (optional)
    ├── requirements.txt         # Agent-specific dependencies (optional)
    ├── README.md                # Agent documentation
    │
    ├── instructions/            # Agent instruction files
    │   ├── mode1_instructions.txt
    │   └── mode2_instructions.txt
    │
    ├── mcp_tools/              # Agent-specific MCP tools
    │   └── custom_tools/
    │
    └── templates/              # Agent templates (optional)
        └── response_templates/
```

---

## 🚀 Creating a New Agent

### Option 1: Using the Template Generator (Recommended)

```bash
./scripts/create_agent.sh <agent_name>
```

This will create a complete agent structure with all necessary files.

### Option 2: Manual Creation

1. **Create agent directory:**
   ```bash
   mkdir -p agents/<agent_name>/instructions
   mkdir -p agents/<agent_name>/mcp_tools
   mkdir -p agents/<agent_name>/templates
   ```

2. **Copy template files:**
   ```bash
   cp agents/daedalus/main.py agents/<agent_name>/main.py
   ```

3. **Update configuration:**
   - Edit `main.py` to define your agent modes
   - Create instruction files in `instructions/`
   - Update `launcher.py` to register your agent

4. **Add agent to launcher:**
   Edit `launcher.py` and add your agent to the `AGENTS` dictionary:
   ```python
   AGENTS = {
       "daedalus": { ... },
       "your_agent": {
           "name": "Your Agent Name",
           "description": "Agent description",
           "emoji": "🤖",
           "path": "agents/your_agent/main.py",
           "modes": ["mode1", "mode2"],
           "default_mode": "mode1",
           "port": 8001
       }
   }
   ```

---

## 📋 Agent Development Guidelines

### Core Principles
1. **Self-contained:** Each agent should be independent
2. **Reusable:** Use `core/` library for common functionality
3. **Documented:** Include comprehensive README
4. **Tested:** Add tests in `tests/unit/test_agents/<agent_name>/`

### Required Files
- ✅ `__init__.py` - Package initialization
- ✅ `main.py` - Chainlit entry point
- ✅ `README.md` - Agent documentation
- ✅ `instructions/` - At least one instruction file

### Recommended Files
- 📝 `config.py` - Agent-specific configuration
- 📦 `requirements.txt` - Additional dependencies
- 🧰 `mcp_tools/` - Custom MCP tools
- 🎨 `templates/` - Response templates

---

## 🔧 Shared Resources

### Core Library (`core/`)
All agents share the core framework:
- Agent factory and configuration
- Session management
- Command routing
- OAuth/SSO handlers
- Qdrant integration

Import from core:
```python
from core import (
    AgentFactory,
    SessionManager,
    CommandRouter,
    SessionUI
)
```

### Shared Utilities (`shared/`)
Common utilities across agents:
- Vector memory management
- Shared MCP tools
- Common data layers

Import from shared:
```python
from shared.vector_memory import create_vector_memory_manager
from shared.mcp_tools.common import AzureTool
```

---

## 🎯 Agent Naming Conventions

Follow Greek mythology theme to match "Pantheon":

- **Daedalus** 🏗️ - Master architect (Azure)
- **Athena** 🛡️ - Wisdom/Security (future)
- **Hermes** 📨 - Messenger/DevOps (future)
- **Hephaestus** 🔨 - Builder/CI-CD (future)
- **Oracle** 🔮 - Analytics/Insights (future)

---

## 📊 Monitoring & Debugging

### View Agent Sessions
```bash
# Launch agent
python launcher.py daedalus

# Use commands in chat
/sessions       # List all sessions
/debug          # Show debug information
/session        # Show current session info
```

### Check Qdrant Collections
Each agent stores sessions in Qdrant. Collection name format:
```
<agent_name>_sessions
```

Example: `daedalus_sessions`

---

## 🧪 Testing

Test structure mirrors agent structure:

```
tests/
├── unit/
│   └── test_agents/
│       ├── test_daedalus/
│       │   ├── test_main.py
│       │   └── test_config.py
│       └── test_your_agent/
│           └── test_main.py
└── integration/
    └── test_agent_integration.py
```

Run tests:
```bash
pytest tests/unit/test_agents/test_daedalus/ -v
```

---

## 📚 Documentation

Each agent should have:

1. **README.md** with:
   - Agent description and purpose
   - Available modes
   - Configuration options
   - Usage examples
   - MCP tools documentation

2. **Inline documentation:**
   - Docstrings for all functions
   - Comments for complex logic
   - Type hints

---

## 🔐 Security & Environment

### Environment Variables
Agent-specific variables should be prefixed:
```bash
# Shared (all agents)
AZURE_OPENAI_API_KEY=...
QDRANT_HOST=localhost

# Agent-specific
DAEDALUS_MODE=platform
SECURITY_SENTINEL_MODE=compliance
```

### Secrets Management
- Never commit secrets
- Use `.env` for local development
- Use Azure Key Vault for production
- Document required environment variables

---

## 📦 Dependencies

### Root Dependencies (`requirements.txt`)
Core dependencies used by all agents

### Agent-Specific Dependencies
Optional `agents/<agent>/requirements.txt` for agent-only packages

Install:
```bash
# Root dependencies
pip install -r requirements.txt

# Agent-specific
pip install -r agents/daedalus/requirements.txt
```

---

## 🎨 UI Customization

Agents share UI resources in `public/`:
- `custom.css` - Styling
- `custom.js` - JavaScript
- `theme.json` - Chainlit theme
- `avatars/` - Agent avatars

Agent-specific avatars:
```
public/avatars/
├── daedalus.png
├── athena.png
└── hermes.png
```

---

## 🚢 Deployment

Each agent can be deployed:

1. **Standalone:** Individual container per agent
2. **Monolithic:** Single deployment with launcher
3. **Serverless:** Azure Container Apps

See `docker/` for deployment configurations.

---

## 📞 Support

For questions or issues:
1. Check agent's README.md
2. Review `docs/BUILDING_NEW_AGENTS.md`
3. Check core library documentation in `core/README.md`

---

*Part of the Pantheon Multi-Agent System* 🏛️
