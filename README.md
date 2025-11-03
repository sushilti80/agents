# 🏗️ Daedalus - Multi-Mode Azure Architecture Assistant

An intelligent Azure architecture assistant powered by Semantic Kernel and Azure OpenAI with Microsoft Entra ID (Azure AD) SSO authentication, persistent session management, and multi-mode architecture expertise.

## ✨ Features

- 🔐 **Enterprise SSO**: Microsoft Entra ID (Azure AD) OAuth authentication with persistent sessions
- 🎭 **Multi-Mode Architecture**: Switch between Platform and Cloud Architect modes on-the-fly
- 💾 **Persistent Sessions**: Resume conversations from thread history sidebar with full context restoration
- 🧠 **RAG-Powered Memory**: Vector-based conversation memory using Qdrant for intelligent context retrieval
- 🌐 **Modern Web Interface**: Beautiful Chainlit UI with custom branding and theme
- 📚 **Microsoft Docs Integration**: Real-time access to official Azure documentation via MCP tools
- � **Advanced Reasoning**: Sequential thinking for complex architecture decisions
- 🎨 **Customizable UI**: Custom logo, themes, and login page branding
- 📊 **Session Management**: Browse, resume, and manage conversation history
- 🚀 **Command System**: Built-in commands for debugging, session info, and mode switching

## 🏛️ Architecture Modes

### 🏢 Platform Architect Mode
- Azure infrastructure and platform services
- Landing zones and enterprise-scale architecture
- Governance, compliance, and security
- DevOps and CI/CD patterns
- Cost optimization strategies

### ☁️ Cloud Architect Mode
- Cloud-native application design
- Microservices and containerization
- Serverless architectures
- Multi-cloud strategies
- Modern application patterns

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Azure OpenAI deployment (GPT-4 or similar)
- Qdrant vector database (for conversation memory)
- Microsoft Entra ID (Azure AD) OAuth application (for SSO)
- Node.js 18+ (for MCP tools)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd agent
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install MCP tools**:
   ```bash
   npm install -g @modelcontextprotocol/server-sequential-thinking
   ```

5. **Start Qdrant**:
   ```bash
   # Using Docker
   docker run -p 6333:6333 qdrant/qdrant
   
   # Or using Podman
   podman run -p 6333:6333 qdrant/qdrant
   ```

6. **Configure Environment Variables**:
   
   Copy `.env.example` to `.env` and configure:
   ```env
   # Azure OpenAI
   AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key-here
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
   AZURE_OPENAI_API_VERSION=2024-05-01-preview
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
   
   # Qdrant Vector Database
   QDRANT_URL=http://localhost:6333
   QDRANT_COLLECTION=agent-conversations
   
   # Microsoft Entra ID OAuth
   OAUTH_AZURE_AD_CLIENT_ID=your-client-id
   OAUTH_AZURE_AD_CLIENT_SECRET=your-client-secret
   OAUTH_AZURE_AD_TENANT_ID=your-tenant-id
   CHAINLIT_AUTH_SECRET=your-random-secret-key
   
   # Optional: Literal AI for monitoring
   LITERAL_API_KEY=your-literal-api-key
   ```

### Running the Agent

**Start Daedalus:**
```bash
chainlit run daedalus.py -w
```

The `-w` flag enables hot-reloading for development.

**Access the UI:**
1. Open your browser to: `http://localhost:8000`
2. Click "Continue with Azure AD" to authenticate
3. Start chatting with Daedalus!

## 📁 Project Structure

```
agent/
├── daedalus.py                          # Main multi-mode agent application
├── agent.py                             # Legacy single-mode agent (deprecated)
├── agent_sso.py                         # SSO-enabled single-mode agent
├── requirements.txt                     # Python dependencies
├── .env                                 # Environment configuration
├── README.md                           # This file
├── BUILDING_NEW_AGENTS.md              # Guide for creating new agents
│
├── .chainlit/                          # Chainlit configuration
│   ├── config.toml                     # Main Chainlit settings
│   └── translations/                   # UI text translations
│       └── en-US.json                  # English translations
│
├── agent_core/                         # Reusable agent framework
│   ├── __init__.py                     # Core exports
│   ├── config.py                       # Configuration classes
│   ├── agent_factory.py                # Agent creation
│   ├── session_manager.py              # Session/conversation management
│   ├── command_router.py               # /command handling
│   ├── session_ui.py                   # Session browser UI
│   ├── oauth_handler.py                # SSO authentication
│   ├── data_layer_factory.py           # Qdrant integration
│   ├── thread_resume_handler.py        # Session restoration
│   ├── monitoring.py                   # QdrantMonitor for RAG metrics
│   └── utils.py                        # Utility functions
│
├── shared/                             # Shared utilities
│   ├── __init__.py
│   ├── vector_memory.py                # Vector memory management
│   └── qdrant_data_layer.py            # Chainlit data layer for Qdrant
│
├── public/                             # Static assets
│   ├── logo.png                        # Custom logo
│   ├── theme.json                      # UI theme configuration
│   ├── custom.css                      # Custom styling
│   └── custom.js                       # Custom JavaScript
│
├── platform_architect_instructions.txt  # Platform mode system prompt
├── ms_cloud_architect_instructions.txt  # Cloud mode system prompt
│
└── tests/                              # Test suite
    ├── test_agent_core.py
    ├── test_sso_integration.py
    └── test_phase4_quick.py
```

## 🎮 Usage Guide

### Switching Modes

Use the `/platform` or `/cloud` commands to switch between architecture modes:

```
User: /platform
Daedalus: ✅ Switched to Platform Architect mode
          Focus: Azure infrastructure, governance, and enterprise patterns

User: /cloud
Daedalus: ✅ Switched to Cloud Architect mode
          Focus: Cloud-native applications and modern patterns
```

### Built-in Commands

- `/platform` - Switch to Platform Architect mode
- `/cloud` - Switch to Cloud Architect mode  
- `/session` - Show current session info and mode
- `/sessions` or `/list` - Browse available sessions
- `/resume <session_id>` - Resume a previous conversation
- `/debug` - Show debug information

### Session Management

**Thread History Sidebar:**
1. Click the sidebar icon (left side of screen)
2. Browse your past conversations
3. Click any session to resume it
4. Sessions are automatically restored with correct mode and context

**Session Restoration:**
- Full conversation history loaded
- Agent mode automatically restored
- Vector memory context preserved
- Seamless continuation of previous discussions

### Example Workflows

**Example 1: Platform Architecture Design**
```
User: I need to design a hub-and-spoke network topology for our enterprise

Daedalus: [In Platform Architect mode]
          [Provides detailed Azure Virtual Network design]
          [Includes VPN Gateway, Azure Firewall, and routing]
          [References Azure Landing Zones best practices]
```

**Example 2: Switch to Cloud-Native Design**
```
User: /cloud

User: How should I design a microservices architecture on AKS?

Daedalus: [In Cloud Architect mode]
          [Provides Kubernetes-native design]
          [Includes service mesh, observability, GitOps]
          [Modern cloud-native patterns]
```

**Example 3: Resume Previous Conversation**
```
User: /sessions
Daedalus: [Shows list of recent conversations]

User: /resume session_abc123
Daedalus: ✅ Restored session: "Azure Landing Zone Discussion"
          [Continues from where you left off]
```

## Architecture

### Components

**Core Application:**
- **daedalus.py**: Multi-mode agent with SSO and session management
- **agent_core/**: Reusable framework for building agents
- **shared/**: Shared utilities (vector memory, data layers)

**System Prompts:**
- **platform_architect_instructions.txt**: Platform mode persona and expertise
- **ms_cloud_architect_instructions.txt**: Cloud mode persona and expertise

**Configuration:**
- **.chainlit/config.toml**: UI settings, OAuth, features
- **.env**: Secrets and environment variables

### Authentication Flow

1. User visits application → Redirected to Microsoft Entra ID login
2. User authenticates with corporate credentials
3. OAuth callback receives user profile (email, name, etc.)
4. User session created with persistent identifier
5. All conversations linked to authenticated user
6. Sessions stored in Qdrant with user metadata

### Session Persistence

**Storage:**
- Conversations stored in Qdrant vector database
- Each message embedded for semantic search
- Thread history accessible via sidebar
- Sessions persist across browser sessions

**Restoration:**
- Click session in sidebar → Full conversation loads
- Agent mode automatically restored
- Vector memory context retrieved
- Seamless continuation

### Vector Memory (RAG)

**Purpose:**
- Intelligent context retrieval from conversation history
- Semantic search across past discussions
- Mode-specific memory filtering
- Enhanced by Azure OpenAI embeddings

**How it works:**
1. Each message embedded using `text-embedding-3-small`
2. Stored in Qdrant with metadata (user, mode, timestamp)
3. Relevant context retrieved for each query
4. Agent has access to related past discussions

### Agent Capabilities

**Both modes can help with:**
- Azure service selection and architecture design
- Security, compliance, and governance best practices
- Cost optimization and resource management
- Best practices from official Microsoft documentation
- Real-time documentation search and code examples

**Platform Architect specializes in:**
- Enterprise-scale landing zones
- Network topology and connectivity
- Identity and access management
- Governance frameworks
- Migration strategies

**Cloud Architect specializes in:**
- Microservices and containerization (AKS, Container Apps)
- Serverless architectures (Functions, Logic Apps)
- Event-driven patterns (Event Grid, Service Bus)
- Cloud-native observability
- DevOps and GitOps patterns

### MCP Tools

**1. Microsoft Learn Documentation** (HTTP Remote Server):
- `microsoft_docs_search` - Search official Microsoft/Azure docs
- `microsoft_docs_fetch` - Fetch complete documentation pages
- `microsoft_code_sample_search` - Find code examples
- Real-time access to latest Azure documentation
- Provides authoritative Microsoft Learn links

**2. Sequential Thinking** (Local npm Server):
- Advanced multi-step reasoning for complex decisions
- Architecture trade-off analysis
- Service comparison and evaluation
- Cost vs. performance optimization
- Breaking down complex requirements

## 🎨 Customization

### UI Branding

**Logo and Theme:**
- Replace `public/logo.png` with your logo
- Edit `public/theme.json` for color scheme
- Modify `public/custom.css` for styling
- Update `public/custom.js` for custom behavior

**Login Page:**
- Configured in `.chainlit/config.toml` under `[UI]`
- `logo_file_url` - Your custom logo
- `login_page_image` - Background image
- `login_page_image_filter` - Image filters for light/dark mode

**Translations:**
- Edit `.chainlit/translations/en-US.json`
- Customize login page title, form labels
- Localize UI text

### Creating New Agents

See **`BUILDING_NEW_AGENTS.md`** for comprehensive guide:

**Approach 1: Standalone Agent**
- Create new agent file from template
- Single-purpose agent with own configuration
- Full SSO, session management, RAG

**Approach 2: Add Mode to Daedalus**
- Add new architecture mode (e.g., "Data Architect")
- Create system prompt file
- Add to `AGENT_MODES` dictionary
- Instant multi-mode capability

### Modify System Prompts

**Platform Architect:**
Edit `platform_architect_instructions.txt`:
- Adjust expertise areas
- Add new service knowledge
- Change response style
- Update architecture patterns

**Cloud Architect:**
Edit `ms_cloud_architect_instructions.txt`:
- Modify cloud-native focus
- Add modern patterns
- Update technology stack
- Change approach to solutions

## 🔧 Configuration

### Chainlit Settings (.chainlit/config.toml)

**Project:**
- `enable_telemetry: false` - Privacy setting
- `session_timeout: 3600` - 1 hour session timeout
- `user_session_timeout: 2592000` - 30 day user session

**Features:**
- `authentication_required: true` - Enforce OAuth/SSO
- `unsafe_allow_html: false` - Security setting
- `edit_message: true` - Allow message editing
- `spontaneous_file_upload: true` - File upload support

**UI:**
- `name` - Assistant display name
- `default_theme` - "light" or "dark"
- `logo_file_url` - Custom logo path
- `custom_css` - Custom stylesheet
- `default_sidebar_state: "open"` - Thread history visible

### OAuth Configuration

**Azure AD Application Setup:**

1. Register application in Azure Portal
2. Configure redirect URI: `http://localhost:8000/auth/oauth/callback`
3. Add API permissions: `User.Read`
4. Create client secret
5. Add to `.env`:
   ```env
   OAUTH_AZURE_AD_CLIENT_ID=<application-id>
   OAUTH_AZURE_AD_CLIENT_SECRET=<client-secret>
   OAUTH_AZURE_AD_TENANT_ID=<tenant-id>
   ```

See `SSO_SETUP_GUIDE.md` for detailed OAuth setup instructions.

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