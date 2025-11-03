# 🏛️ Pantheon - Multi-Agent Architecture System# 🏗️ Daedalus - Multi-Mode Azure Architecture Assistant



> *Home of intelligent agents for cloud architecture, DevOps, security, and more*An intelligent Azure architecture assistant powered by Agentic Framework and Azure OpenAI with Microsoft Entra ID (Azure AD) SSO authentication, persistent session management, and multi-mode architecture expertise.



A sophisticated multi-agent platform powered by Azure OpenAI, featuring enterprise SSO, persistent session management, and a modular architecture for building specialized AI assistants.## ✨ Features



[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)- 🔐 **Enterprise SSO**: Microsoft Entra ID (Azure AD) OAuth authentication with persistent sessions

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)- 🎭 **Multi-Mode Architecture**: Switch between Platform and Cloud Architect modes on-the-fly

[![Chainlit](https://img.shields.io/badge/chainlit-latest-green.svg)](https://docs.chainlit.io/)- 💾 **Persistent Sessions**: Resume conversations from thread history sidebar with full context restoration

- 🧠 **RAG-Powered Memory**: Vector-based conversation memory using Qdrant for intelligent context retrieval

## ✨ Key Features- 🌐 **Modern Web Interface**: Beautiful Chainlit UI with custom branding and theme

- 📚 **Microsoft Docs Integration**: Real-time access to official Azure documentation via MCP tools

- 🏛️ **Multi-Agent System**: Extensible framework for deploying multiple specialized agents- � **Advanced Reasoning**: Sequential thinking for complex architecture decisions

- 🔐 **Enterprise SSO**: Microsoft Entra ID (Azure AD) OAuth authentication- 🎨 **Customizable UI**: Custom logo, themes, and login page branding

- 🎭 **Multi-Mode Agents**: Each agent supports multiple specialized modes- 📊 **Session Management**: Browse, resume, and manage conversation history

- 💾 **Persistent Memory**: Vector-based conversation history using Qdrant- 🚀 **Command System**: Built-in commands for debugging, session info, and mode switching

- 🌐 **Modern Web Interface**: Beautiful Chainlit UI with custom branding

- 📚 **MCP Tools**: Model Context Protocol integration for extended capabilities## 🏛️ Architecture Modes

- 🚀 **Easy Deployment**: Docker support and Azure-ready configurations

- 🧩 **Modular Design**: Shared core framework with agent-specific customizations### 🏢 Platform Architect Mode

- 📊 **Session Management**: Browse, resume, and restore conversation history- Azure infrastructure and platform services

- 🧠 **Advanced Reasoning**: Sequential thinking for complex decisions- Landing zones and enterprise-scale architecture

- Governance, compliance, and security

## 🤖 Available Agents- DevOps and CI/CD patterns

- Cost optimization strategies

### 🏗️ Daedalus - Azure Architecture Assistant

**Status:** ✅ Active  ### ☁️ Cloud Architect Mode

**Location:** [`agents/daedalus/`](agents/daedalus/)  - Cloud-native application design

**Modes:** Platform Architect, MS Cloud Architect  - Microservices and containerization

**Port:** 8000- Serverless architectures

- Multi-cloud strategies

Azure cloud architecture guidance, best practices, and implementation strategies.- Modern application patterns



**Quick Start:**## 🚀 Quick Start

```bash

python launcher.py daedalus### Prerequisites

```

- Python 3.12+

[📖 Daedalus Documentation](agents/daedalus/README.md)- Azure OpenAI deployment (GPT-4 or similar)

- Qdrant vector database (for conversation memory)

---- Microsoft Entra ID (Azure AD) OAuth application (for SSO)

- Node.js 18+ (for MCP tools)

### 🆕 Create Your Own Agent

### Installation

Use the agent generator to scaffold a new agent in minutes:

1. **Clone the repository**:

```bash   ```bash

./scripts/create_agent.sh security_sentinel 🛡️ "Cloud security advisor"   git clone <your-repo-url>

```   cd agent

   ```

[📖 Agent Creation Guide](agents/README.md)

2. **Create virtual environment**:

## 📁 Project Structure   ```bash

   python -m venv venv

```   source venv/bin/activate  # On Windows: venv\Scripts\activate

pantheon/   ```

├── agents/                     # Individual agent implementations

│   ├── daedalus/              # Azure Architecture Assistant3. **Install Python dependencies**:

│   │   ├── main.py            # Agent entry point   ```bash

│   │   ├── instructions/      # Agent instruction files   pip install -r requirements.txt

│   │   ├── mcp_tools/        # Agent-specific MCP tools   ```

│   │   └── README.md         # Agent documentation

│   └── README.md             # Agent development guide4. **Install MCP tools**:

│   ```bash

├── core/                      # Shared agent framework   npm install -g @modelcontextprotocol/server-sequential-thinking

│   ├── agent_factory.py      # Agent creation and setup   ```

│   ├── session_manager.py    # Session management

│   ├── command_handlers.py   # Command routing5. **Start Qdrant**:

│   ├── oauth_handler.py      # SSO authentication   ```bash

│   └── README.md             # Core library docs   # Using Docker

│   docker run -p 6333:6333 qdrant/qdrant

├── shared/                    # Cross-agent utilities   

│   ├── vector_memory.py      # Qdrant vector memory   # Or using Podman

│   ├── qdrant_data_layer.py  # Data layer implementation   podman run -p 6333:6333 qdrant/qdrant

│   └── mcp_tools/            # Shared MCP tools   ```

│

├── scripts/                   # Utility scripts6. **Configure Environment Variables**:

│   ├── start_daedalus.sh     # Launch Daedalus   

│   └── create_agent.sh       # Agent generator   Copy `.env.example` to `.env` and configure:

│   ```env

├── public/                    # UI assets   # Azure OpenAI

│   ├── custom.css            # Custom styles   AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/

│   ├── theme.json            # Chainlit theme   AZURE_OPENAI_API_KEY=your-api-key-here

│   └── avatars/              # Agent avatars   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

│   AZURE_OPENAI_API_VERSION=2024-05-01-preview

├── docs/                      # Documentation   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small

│   ├── BUILDING_NEW_AGENTS.md   

│   └── architecture/   # Qdrant Vector Database

│   QDRANT_URL=http://localhost:6333

├── tests/                     # Test suite   QDRANT_COLLECTION=agent-conversations

│   ├── unit/   

│   └── integration/   # Microsoft Entra ID OAuth

│   OAUTH_AZURE_AD_CLIENT_ID=your-client-id

├── launcher.py                # Multi-agent launcher   OAUTH_AZURE_AD_CLIENT_SECRET=your-client-secret

├── requirements.txt           # Python dependencies   OAUTH_AZURE_AD_TENANT_ID=your-tenant-id

├── .env.example              # Environment template   CHAINLIT_AUTH_SECRET=your-random-secret-key

└── README.md                 # This file   

```   # Optional: Literal AI for monitoring

   LITERAL_API_KEY=your-literal-api-key

## 🚀 Quick Start   ```



### Prerequisites### Running the Agent



- **Python 3.12+****Start Daedalus:**

- **Azure OpenAI** deployment (GPT-4 or similar)```bash

- **Qdrant** vector databasechainlit run daedalus.py -w

- **Microsoft Entra ID** (Azure AD) OAuth app (for SSO)```

- **Node.js 18+** (for MCP tools)

The `-w` flag enables hot-reloading for development.

### Installation

**Access the UI:**

1. **Clone the repository:**1. Open your browser to: `http://localhost:8000`

   ```bash2. Click "Continue with Azure AD" to authenticate

   git clone https://github.com/sushilti80/agents.git3. Start chatting with Daedalus!

   cd agents

   ```## 📁 Project Structure



2. **Create virtual environment:**```

   ```bashagent/

   python -m venv venv├── daedalus.py                          # Main multi-mode agent application

   source venv/bin/activate  # On Windows: venv\Scripts\activate├── agent.py                             # Legacy single-mode agent (deprecated)

   ```├── agent_sso.py                         # SSO-enabled single-mode agent

├── requirements.txt                     # Python dependencies

3. **Install dependencies:**├── .env                                 # Environment configuration

   ```bash├── README.md                           # This file

   pip install -r requirements.txt├── BUILDING_NEW_AGENTS.md              # Guide for creating new agents

   ```│

├── .chainlit/                          # Chainlit configuration

4. **Install MCP tools:**│   ├── config.toml                     # Main Chainlit settings

   ```bash│   └── translations/                   # UI text translations

   npm install -g @modelcontextprotocol/server-sequential-thinking│       └── en-US.json                  # English translations

   ```│

├── agent_core/                         # Reusable agent framework

5. **Start Qdrant:**│   ├── __init__.py                     # Core exports

   ```bash│   ├── config.py                       # Configuration classes

   docker run -p 6333:6333 qdrant/qdrant│   ├── agent_factory.py                # Agent creation

   ```│   ├── session_manager.py              # Session/conversation management

│   ├── command_router.py               # /command handling

6. **Configure environment:**│   ├── session_ui.py                   # Session browser UI

   ```bash│   ├── oauth_handler.py                # SSO authentication

   cp .env.example .env│   ├── data_layer_factory.py           # Qdrant integration

   # Edit .env with your credentials│   ├── thread_resume_handler.py        # Session restoration

   ```│   ├── monitoring.py                   # QdrantMonitor for RAG metrics

│   └── utils.py                        # Utility functions

7. **Launch an agent:**│

   ```bash├── shared/                             # Shared utilities

   # List available agents│   ├── __init__.py

   python launcher.py --list│   ├── vector_memory.py                # Vector memory management

   │   └── qdrant_data_layer.py            # Chainlit data layer for Qdrant

   # Launch Daedalus│

   python launcher.py daedalus├── public/                             # Static assets

   ```│   ├── logo.png                        # Custom logo

│   ├── theme.json                      # UI theme configuration

8. **Open browser:**│   ├── custom.css                      # Custom styling

   ```│   └── custom.js                       # Custom JavaScript

   http://localhost:8000│

   ```├── platform_architect_instructions.txt  # Platform mode system prompt

├── ms_cloud_architect_instructions.txt  # Cloud mode system prompt

## ⚙️ Configuration│

└── tests/                              # Test suite

### Environment Variables    ├── test_agent_core.py

    ├── test_sso_integration.py

Create a `.env` file in the project root:    └── test_phase4_quick.py

```

```env

# Azure OpenAI## 🎮 Usage Guide

AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/

AZURE_OPENAI_API_KEY=your-api-key### Switching Modes

AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

AZURE_OPENAI_API_VERSION=2024-05-01-previewUse the `/platform` or `/cloud` commands to switch between architecture modes:

AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small

```

# Qdrant Vector DatabaseUser: /platform

QDRANT_URL=http://localhost:6333Daedalus: ✅ Switched to Platform Architect mode

QDRANT_COLLECTION=pantheon-sessions          Focus: Azure infrastructure, governance, and enterprise patterns



# Microsoft Entra ID OAuth (SSO)User: /cloud

OAUTH_AZURE_AD_CLIENT_ID=your-client-idDaedalus: ✅ Switched to Cloud Architect mode

OAUTH_AZURE_AD_CLIENT_SECRET=your-client-secret          Focus: Cloud-native applications and modern patterns

OAUTH_AZURE_AD_TENANT_ID=your-tenant-id```

CHAINLIT_AUTH_SECRET=your-random-secret-key

### Built-in Commands

# Optional: Literal AI monitoring

LITERAL_API_KEY=your-literal-api-key- `/platform` - Switch to Platform Architect mode

```- `/cloud` - Switch to Cloud Architect mode  

- `/session` - Show current session info and mode

See [`.env.example`](.env.example) for a complete template.- `/sessions` or `/list` - Browse available sessions

- `/resume <session_id>` - Resume a previous conversation

## 🎮 Using the Launcher- `/debug` - Show debug information



The Pantheon launcher provides a unified interface for all agents:### Session Management



### List Available Agents**Thread History Sidebar:**

```bash1. Click the sidebar icon (left side of screen)

python launcher.py --list2. Browse your past conversations

```3. Click any session to resume it

4. Sessions are automatically restored with correct mode and context

### Launch an Agent

```bash**Session Restoration:**

# Basic launch- Full conversation history loaded

python launcher.py daedalus- Agent mode automatically restored

- Vector memory context preserved

# Specify mode- Seamless continuation of previous discussions

python launcher.py daedalus --mode platform

### Example Workflows

# Custom port

python launcher.py daedalus --port 8080**Example 1: Platform Architecture Design**

```

# Disable auto-reloadUser: I need to design a hub-and-spoke network topology for our enterprise

python launcher.py daedalus --no-watch

```Daedalus: [In Platform Architect mode]

          [Provides detailed Azure Virtual Network design]

### Help          [Includes VPN Gateway, Azure Firewall, and routing]

```bash          [References Azure Landing Zones best practices]

python launcher.py --help```

```

**Example 2: Switch to Cloud-Native Design**

## 💬 Chat Commands```

User: /cloud

All agents support these commands:

User: How should I design a microservices architecture on AKS?

| Command | Description |

|---------|-------------|Daedalus: [In Cloud Architect mode]

| `/sessions` or `/list` | View all your previous sessions |          [Provides Kubernetes-native design]

| `/debug` | Show debug information and session stats |          [Includes service mesh, observability, GitOps]

| `/session` | Display current session information |          [Modern cloud-native patterns]

| `/resume <id>` | Resume a previous session by ID |```

| `/<mode>` | Switch to a different agent mode |

**Example 3: Resume Previous Conversation**

## 🛠️ Development```

User: /sessions

### Creating a New AgentDaedalus: [Shows list of recent conversations]



1. **Use the generator:**User: /resume session_abc123

   ```bashDaedalus: ✅ Restored session: "Azure Landing Zone Discussion"

   ./scripts/create_agent.sh my_agent 🤖 "My agent description"          [Continues from where you left off]

   ``````



2. **Update instruction files:**## Architecture

   ```bash

   vim agents/my_agent/instructions/default_instructions.txt### Components

   ```

**Core Application:**

3. **Register in launcher:**- **daedalus.py**: Multi-mode agent with SSO and session management

   Edit `launcher.py` and add your agent to the `AGENTS` dictionary.- **agent_core/**: Reusable framework for building agents

- **shared/**: Shared utilities (vector memory, data layers)

4. **Test the agent:**

   ```bash**System Prompts:**

   python launcher.py my_agent- **platform_architect_instructions.txt**: Platform mode persona and expertise

   ```- **ms_cloud_architect_instructions.txt**: Cloud mode persona and expertise



See [Agent Development Guide](agents/README.md) for detailed instructions.**Configuration:**

- **.chainlit/config.toml**: UI settings, OAuth, features

### Running Tests- **.env**: Secrets and environment variables



```bash### Authentication Flow

# All tests

pytest tests/ -v1. User visits application → Redirected to Microsoft Entra ID login

2. User authenticates with corporate credentials

# Specific agent tests3. OAuth callback receives user profile (email, name, etc.)

pytest tests/unit/test_agents/test_daedalus/ -v4. User session created with persistent identifier

5. All conversations linked to authenticated user

# With coverage6. Sessions stored in Qdrant with user metadata

pytest tests/ --cov=core --cov=agents --cov-report=html

```### Session Persistence



### Code Quality**Storage:**

- Conversations stored in Qdrant vector database

```bash- Each message embedded for semantic search

# Format code- Thread history accessible via sidebar

black .- Sessions persist across browser sessions



# Lint**Restoration:**

flake8 .- Click session in sidebar → Full conversation loads

- Agent mode automatically restored

# Type checking- Vector memory context retrieved

mypy core/ agents/- Seamless continuation

```

### Vector Memory (RAG)

## 📚 Documentation

**Purpose:**

- [**Agent Development Guide**](agents/README.md) - Create new agents- Intelligent context retrieval from conversation history

- [**Core Library Reference**](core/README.md) - Framework documentation- Semantic search across past discussions

- [**Building New Agents**](docs/BUILDING_NEW_AGENTS.md) - Comprehensive guide- Mode-specific memory filtering

- [**Daedalus Documentation**](agents/daedalus/README.md) - Azure Architecture Assistant- Enhanced by Azure OpenAI embeddings



## 🏗️ Architecture**How it works:**

1. Each message embedded using `text-embedding-3-small`

Pantheon follows a modular, agent-centric architecture:2. Stored in Qdrant with metadata (user, mode, timestamp)

3. Relevant context retrieved for each query

```4. Agent has access to related past discussions

┌─────────────────────────────────────────────────┐

│              Pantheon Launcher                  │### Agent Capabilities

└─────────────────────────────────────────────────┘

                      │**Both modes can help with:**

        ┌─────────────┼─────────────┐- Azure service selection and architecture design

        ▼             ▼             ▼- Security, compliance, and governance best practices

   ┌─────────┐  ┌─────────┐  ┌─────────┐- Cost optimization and resource management

   │Daedalus │  │ Agent 2 │  │ Agent N │- Best practices from official Microsoft documentation

   └─────────┘  └─────────┘  └─────────┘- Real-time documentation search and code examples

        │             │             │

        └─────────────┼─────────────┘**Platform Architect specializes in:**

                      ▼- Enterprise-scale landing zones

        ┌───────────────────────────┐- Network topology and connectivity

        │      Core Framework        │- Identity and access management

        │  • AgentFactory            │- Governance frameworks

        │  • SessionManager          │- Migration strategies

        │  • CommandRouter           │

        │  • OAuthHandler            │**Cloud Architect specializes in:**

        └───────────────────────────┘- Microservices and containerization (AKS, Container Apps)

                      │- Serverless architectures (Functions, Logic Apps)

        ┌─────────────┼─────────────┐- Event-driven patterns (Event Grid, Service Bus)

        ▼             ▼             ▼- Cloud-native observability

   ┌─────────┐  ┌─────────┐  ┌─────────┐- DevOps and GitOps patterns

   │ Qdrant  │  │Azure OAI│  │   MCP   │

   │ Memory  │  │   API   │  │  Tools  │### MCP Tools

   └─────────┘  └─────────┘  └─────────┘

```**1. Microsoft Learn Documentation** (HTTP Remote Server):

- `microsoft_docs_search` - Search official Microsoft/Azure docs

### Key Components- `microsoft_docs_fetch` - Fetch complete documentation pages

- `microsoft_code_sample_search` - Find code examples

- **Launcher**: Multi-agent orchestrator- Real-time access to latest Azure documentation

- **Agents**: Specialized AI assistants- Provides authoritative Microsoft Learn links

- **Core**: Shared framework and utilities

- **Shared**: Common resources (memory, tools)**2. Sequential Thinking** (Local npm Server):

- **Qdrant**: Vector database for conversations- Advanced multi-step reasoning for complex decisions

- **Azure OpenAI**: LLM backend- Architecture trade-off analysis

- **MCP Tools**: Extended capabilities- Service comparison and evaluation

- Cost vs. performance optimization

## 🚢 Deployment- Breaking down complex requirements



### Docker## 🎨 Customization



```bash### UI Branding

# Build

docker build -t pantheon:latest .**Logo and Theme:**

- Replace `public/logo.png` with your logo

# Run- Edit `public/theme.json` for color scheme

docker run -p 8000:8000 --env-file .env pantheon:latest- Modify `public/custom.css` for styling

```- Update `public/custom.js` for custom behavior



### Azure Container Apps**Login Page:**

- Configured in `.chainlit/config.toml` under `[UI]`

```bash- `logo_file_url` - Your custom logo

# Deploy- `login_page_image` - Background image

az containerapp up \- `login_page_image_filter` - Image filters for light/dark mode

  --name pantheon \

  --resource-group my-rg \**Translations:**

  --image pantheon:latest \- Edit `.chainlit/translations/en-US.json`

  --env-vars @.env \- Customize login page title, form labels

  --ingress external \- Localize UI text

  --target-port 8000

```### Creating New Agents



See [`docker/`](docker/) for deployment configurations.See **`BUILDING_NEW_AGENTS.md`** for comprehensive guide:



## 🔐 Security**Approach 1: Standalone Agent**

- Create new agent file from template

- **SSO Authentication**: Azure AD OAuth 2.0- Single-purpose agent with own configuration

- **Session Encryption**: Secure session tokens- Full SSO, session management, RAG

- **Environment Secrets**: Never commit `.env`

- **API Key Rotation**: Regular credential updates**Approach 2: Add Mode to Daedalus**

- **User Isolation**: Sessions scoped per user- Add new architecture mode (e.g., "Data Architect")

- Create system prompt file

## 🤝 Contributing- Add to `AGENT_MODES` dictionary

- Instant multi-mode capability

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Modify System Prompts

### Development Workflow

**Platform Architect:**

1. Fork the repositoryEdit `platform_architect_instructions.txt`:

2. Create a feature branch- Adjust expertise areas

3. Make your changes- Add new service knowledge

4. Run tests and linting- Change response style

5. Submit a pull request- Update architecture patterns



## 📝 License**Cloud Architect:**

Edit `ms_cloud_architect_instructions.txt`:

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.- Modify cloud-native focus

- Add modern patterns

## 🙏 Acknowledgments- Update technology stack

- Change approach to solutions

- **Chainlit** - Web UI framework

- **Semantic Kernel** - Agent framework## 🔧 Configuration

- **Qdrant** - Vector database

- **Azure OpenAI** - LLM backend### Chainlit Settings (.chainlit/config.toml)

- **MCP** - Model Context Protocol

**Project:**

## 📊 Roadmap- `enable_telemetry: false` - Privacy setting

- `session_timeout: 3600` - 1 hour session timeout

- [x] Daedalus Azure Architecture Agent- `user_session_timeout: 2592000` - 30 day user session

- [x] Multi-agent launcher

- [x] Agent generator script**Features:**

- [ ] Security Sentinel agent- `authentication_required: true` - Enforce OAuth/SSO

- [ ] DevOps Hermes agent- `unsafe_allow_html: false` - Security setting

- [ ] Analytics Oracle agent- `edit_message: true` - Allow message editing

- [ ] Multi-tenant support- `spontaneous_file_upload: true` - File upload support

- [ ] Agent marketplace

- [ ] Plugin system**UI:**

- `name` - Assistant display name

## 📞 Support- `default_theme` - "light" or "dark"

- `logo_file_url` - Custom logo path

- **Documentation**: Check the [docs/](docs/) directory- `custom_css` - Custom stylesheet

- **Issues**: [GitHub Issues](https://github.com/sushilti80/agents/issues)- `default_sidebar_state: "open"` - Thread history visible

- **Discussions**: [GitHub Discussions](https://github.com/sushilti80/agents/discussions)

### OAuth Configuration

## 🌟 Star History

**Azure AD Application Setup:**

If you find Pantheon useful, please consider giving it a star! ⭐

1. Register application in Azure Portal

---2. Configure redirect URI: `http://localhost:8000/auth/oauth/callback`

3. Add API permissions: `User.Read`

<div align="center">4. Create client secret

5. Add to `.env`:

**Built with ❤️ by the Pantheon Team**   ```env

   OAUTH_AZURE_AD_CLIENT_ID=<application-id>

🏛️ *Pantheon - Where Intelligent Agents Live* 🏛️   OAUTH_AZURE_AD_CLIENT_SECRET=<client-secret>

   OAUTH_AZURE_AD_TENANT_ID=<tenant-id>

[Documentation](docs/) • [Agents](agents/) • [Contributing](CONTRIBUTING.md) • [License](LICENSE)   ```



</div>See `SSO_SETUP_GUIDE.md` for detailed OAuth setup instructions.


### Qdrant Configuration

**Local Development:**
```env
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=agent-conversations
```

**Production:**
```env
QDRANT_URL=https://your-qdrant-cluster.io
QDRANT_API_KEY=your-api-key
QDRANT_COLLECTION=agent-conversations
```

### Azure OpenAI Settings

**Model Configuration:**
```python
# In daedalus.py - AgentConfig
temperature=0.2          # Creativity level (0.0-1.0)
max_tokens=4096         # Response length limit
```

**Deployment Names:**
- Chat: `gpt-4`, `gpt-4o`, or your deployment name
- Embeddings: `text-embedding-3-small` or similar

## 🐛 Troubleshooting

### Authentication Issues

**OAuth callback error:**
- Verify redirect URI matches Azure AD configuration
- Check client ID and secret in `.env`
- Review logs for detailed error messages

**"Missing async/await" error:**
- Fixed in latest version - ensure `oauth_callback` is `async`
- Update `daedalus.py` if using older version

**Session not authenticated:**
- Clear browser cache and cookies
- Check `CHAINLIT_AUTH_SECRET` is set
- Verify Azure AD app permissions

### Session Management Issues

**Sessions not appearing in sidebar:**
- Ensure Qdrant is running and accessible
- Check `QDRANT_URL` and `QDRANT_COLLECTION`
- Verify user is authenticated (sessions are user-specific)

**Mode not restored when resuming:**
- Latest version restores mode automatically
- Check logs for "Restoring agent mode" message
- Verify agent recreation in session restoration

**Duplicate welcome messages:**
- Should not occur in current version
- If seen, clear browser localStorage
- Restart Chainlit application

### Vector Memory / RAG Issues

**Qdrant connection failed:**
```bash
# Start Qdrant if not running
docker run -p 6333:6333 qdrant/qdrant

# Verify connection
curl http://localhost:6333
```

**Embedding deployment not found:**
- Check `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` in `.env`
- Verify deployment exists in Azure OpenAI
- Use `text-embedding-3-small` or similar model

**Memory not working:**
- Check logs for "VectorMemoryManager initialized"
- Verify collection creation: `Collection: agent-conversations`
- Test Qdrant UI: `http://localhost:6333/dashboard`

### UI Customization Issues

**Logo not showing on login page:**
- Use relative path: `/public/logo.png`
- Not absolute URL for local development
- Hard refresh browser: `Cmd+Shift+R` or `Ctrl+Shift+R`
- Check file exists: `agent/public/logo.png`

**CSS changes not applied:**
- Clear browser cache
- Verify path in config.toml: `custom_css = "/public/custom.css"`
- Check browser DevTools console for errors

**Theme not loading:**
- Verify `custom_theme` path in config.toml
- Check `theme.json` syntax is valid JSON
- Use relative path for local: `/public/theme.json`

### MCP Tool Issues

**Sequential Thinking not available:**
```bash
# Install globally
npm install -g @modelcontextprotocol/server-sequential-thinking

# Verify installation
which npx
```

**Microsoft Docs search not working:**
- Check internet connection
- Verify MCP server configuration
- Review logs for HTTP errors

### General Debugging

**Enable debug logging:**
```python
# In daedalus.py
logger = setup_logging("daedalus.log", logging.DEBUG)
```

**Check logs:**
```bash
tail -f daedalus.log
```

**Common log messages:**
- ✅ `OAuth configuration loaded successfully` - SSO ready
- ✅ `VectorMemoryManager initialized` - RAG ready
- ✅ `Creating agent in X mode` - Agent created
- ⚠️ `Missing OAuth environment variables` - Check `.env`
- ❌ `Error creating user` - OAuth callback issue

## 📚 Documentation

- **README.md** - This file (main documentation)
- **BUILDING_NEW_AGENTS.md** - Complete guide for creating new agents
- **SSO_SETUP_GUIDE.md** - Detailed OAuth/SSO configuration
- **DEPENDENCY_ORGANIZATION_COMPLETE.md** - Code organization and architecture
- **CODE_REORGANIZATION_SUMMARY.md** - Migration details for shared/ structure

## 🧪 Testing

**Run unit tests:**
```bash
pytest tests/test_agent_core.py -v
```

**Run SSO integration tests:**
```bash
pytest tests/test_sso_integration.py -v
```

**Run quick validation:**
```bash
python test_phase4_quick.py
```

**Manual testing checklist:**
- [ ] Authentication with Azure AD
- [ ] Mode switching (/platform, /cloud)
- [ ] Session restoration from sidebar
- [ ] Vector memory context retrieval
- [ ] MCP tool invocation (docs search, sequential thinking)
- [ ] Custom commands (/session, /sessions, /resume)
- [ ] UI customization (logo, theme)

## 🐳 Containerized Deployment

Build and run using Docker/Podman:

```bash
# Build image
podman build -t daedalus-agent:latest .

# Run with environment file
podman run --env-file .env \
  -p 8000:8000 \
  -v ./public:/app/public:ro \
  daedalus-agent:latest
```

**Production .env example:**
```env
AZURE_OPENAI_ENDPOINT=https://prod-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small

QDRANT_URL=https://your-qdrant-cluster.io
QDRANT_API_KEY=<your-qdrant-key>
QDRANT_COLLECTION=agent-conversations

OAUTH_AZURE_AD_CLIENT_ID=<client-id>
OAUTH_AZURE_AD_CLIENT_SECRET=<client-secret>
OAUTH_AZURE_AD_TENANT_ID=<tenant-id>
CHAINLIT_AUTH_SECRET=<random-secret>
```

**Security Notes:**
- Never commit `.env` to version control
- Use secrets management in production
- Rotate OAuth secrets regularly
- Validate allowed origins for CORS

## 🏗️ Development

### Hot Reload

Enable automatic reloading during development:
```bash
chainlit run daedalus.py -w
```

Changes to these files trigger reload:
- `daedalus.py`
- `agent_core/**/*.py`
- `shared/**/*.py`
- System prompt files (`.txt`)
- `.chainlit/config.toml`

### Adding New Features

**1. Add new mode:**
- Create system prompt file: `new_mode_instructions.txt`
- Add to `AGENT_MODES` in `daedalus.py`
- Add command handler: `/new_mode`
- Test mode switching and restoration

**2. Add custom command:**
- Define in `CommandConfig`
- Implement handler in `command_router.py`
- Add to command list display
- Document in README

**3. Customize UI:**
- Edit `public/custom.css` for styling
- Modify `public/theme.json` for colors
- Update `public/custom.js` for behavior
- Configure `.chainlit/config.toml`

### Code Organization

**agent_core/** - Reusable framework:
- `config.py` - Configuration dataclasses
- `agent_factory.py` - Agent creation and mode management
- `session_manager.py` - Session/conversation lifecycle
- `command_router.py` - Command processing
- `session_ui.py` - Session browser and restoration UI
- `oauth_handler.py` - SSO authentication
- `data_layer_factory.py` - Qdrant integration
- `thread_resume_handler.py` - Session restoration logic
- `monitoring.py` - Performance metrics
- `utils.py` - Helper functions

**shared/** - Cross-cutting utilities:
- `vector_memory.py` - Vector memory management
- `qdrant_data_layer.py` - Chainlit data layer implementation

**Benefits:**
- ✅ Clean separation of concerns
- ✅ Reusable across multiple agents
- ✅ Easy to test and maintain
- ✅ No circular dependencies

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes with tests
4. Update documentation
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open Pull Request

**Code Style:**
- Follow PEP 8 guidelines
- Add type hints
- Include docstrings
- Write tests for new features

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

- **Microsoft Semantic Kernel** - Agent framework
- **Chainlit** - Modern chat UI framework
- **Azure OpenAI** - LLM and embeddings
- **Qdrant** - Vector database for RAG
- **MCP (Model Context Protocol)** - Tool integration standard

## MCP SDK Entry Point Shim
Version 1.20.1 of `@modelcontextprotocol/sdk` lacked root `dist/esm/index.js` and `dist/cjs/index.js` referenced in its `package.json` exports. The Dockerfile writes deterministic shim files exporting from `client` and `server` submodules, then places the scope under `/app/node_modules` and symlinks `/usr/bin/node_modules` so the sequential thinking server (installed in `/usr/bin`) can resolve the package under Node ESM rules.

If future releases restore proper entrypoints, you can remove:
- The shim creation RUN step in the builder stage.
- The copy of `@modelcontextprotocol` into `/app/node_modules`.
- The symlink `ln -s /app/node_modules /usr/bin/node_modules`.

## Security Hardening
- Secrets are no longer baked into the image; the Dockerfile now sets `AZURE_OPENAI_API_KEY=__INJECT_AT_RUNTIME__`.
- Always inject the real key at runtime via `--env-file` or your orchestrator’s secret manager.
- Consider pinning MCP package versions for reproducibility.
- Add a startup verification script (optional) to assert MCP connectivity before serving traffic.

## Quick Verification Inside Container
```bash
podman exec -it sk-agent node -e "import('@modelcontextprotocol/sdk').then(m=>console.log('MCP OK', Object.keys(m))).catch(e=>console.error(e))"
```

## Next Steps
1. Open upstream issue describing missing entrypoints (attach shim approach).
2. Add integration tests for tool invocation.
3. Swap HEALTHCHECK to a lightweight Python endpoint or enable Docker format if using Podman.