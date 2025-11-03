# 🏗️ Daedalus - Azure Architecture Assistant

> *Master architect of the Pantheon system, specializing in Azure cloud architecture and best practices*

## Overview

Daedalus is an intelligent Azure architecture assistant that provides guidance on cloud infrastructure design, best practices, and implementation strategies. Named after the legendary Greek architect and craftsman, Daedalus helps you build robust, scalable cloud solutions.

## 🎯 Key Features

- **Multi-Mode Architecture:** Switch between Platform and Cloud architect modes
- **Azure Expertise:** Deep knowledge of Azure services and patterns
- **Best Practices:** Incorporates Microsoft's Well-Architected Framework
- **Session Memory:** Persistent conversation history via Qdrant
- **SSO Integration:** Azure AD authentication support
- **Interactive UI:** Web-based Chainlit interface

## 🚀 Quick Start

### Using Pantheon Launcher (Recommended)
```bash
# From project root
python launcher.py daedalus

# With specific mode
python launcher.py daedalus --mode platform

# On custom port
python launcher.py daedalus --port 8080
```

### Using Start Script
```bash
./scripts/start_daedalus.sh
```

### Direct Launch
```bash
chainlit run agents/daedalus/main.py -w
```

## 🎭 Agent Modes

### 🏗️ Platform Architect
**Focus:** Azure platform architecture with Aya service catalog integration

**Use Cases:**
- Infrastructure design
- Landing zone architecture
- Azure service selection
- Platform engineering

**Instruction File:** `instructions/platform_architect_instructions.txt`

### ☁️ MS Cloud Architect
**Focus:** Broader Microsoft cloud solutions (Azure, M365, Power Platform)

**Use Cases:**
- Multi-cloud strategy
- Microsoft 365 integration
- Power Platform solutions
- Hybrid cloud architecture

**Instruction File:** `instructions/ms_cloud_architect_instructions.txt`

## 📋 Configuration

### Environment Variables

Required:
```bash
# Azure OpenAI
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your_deployment_name

# Qdrant (Vector Database)
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

Optional:
```bash
# SSO/OAuth
OAUTH_AZURE_CLIENT_ID=your_client_id
OAUTH_AZURE_CLIENT_SECRET=your_client_secret
OAUTH_AZURE_TENANT_ID=your_tenant_id

# Agent Configuration
DAEDALUS_DEFAULT_MODE=platform
DAEDALUS_TEMPERATURE=0.2
DAEDALUS_LOG_LEVEL=INFO
```

### Agent Configuration

Located in `main.py`:

```python
DAEDALUS_CONFIG = AgentConfig(
    agent_name="Daedalus",
    agent_modes=AGENT_MODES,
    default_mode="platform",
    session_config=SessionConfig(
        max_sessions_query=100,
        max_sessions_display=10,
        max_history_messages=100
    ),
    temperature=0.2
)
```

## 💬 Chat Commands

| Command | Description |
|---------|-------------|
| `/sessions` or `/list` | View all your previous sessions |
| `/debug` | Show debug information and session stats |
| `/session` | Display current session information |
| `/resume <session_id>` | Resume a previous session |
| `/platform` | Switch to Platform Architect mode |
| `/cloud` | Switch to MS Cloud Architect mode |

## 🗂️ Directory Structure

```
agents/daedalus/
├── __init__.py                              # Package initialization
├── main.py                                  # Main agent entry point
├── README.md                                # This file
│
├── instructions/                            # Agent instructions
│   ├── platform_architect_instructions.txt  # Platform mode instructions
│   └── ms_cloud_architect_instructions.txt  # Cloud mode instructions
│
├── mcp_tools/                               # Daedalus-specific MCP tools
│   └── (future custom tools)
│
└── templates/                               # Response templates
    └── (future templates)
```

## 🔧 Dependencies

Daedalus uses dependencies from the root `requirements.txt`:

Core dependencies:
- `chainlit` - Web UI framework
- `semantic-kernel` - Agent framework
- `qdrant-client` - Vector database
- `python-dotenv` - Environment management

Shared libraries:
- `core` - Agent framework (session, commands, factory)
- `shared` - Vector memory and utilities

## 🧪 Testing

Run Daedalus tests:

```bash
# All Daedalus tests
pytest tests/unit/test_agents/test_daedalus/ -v

# Specific test
pytest tests/unit/test_agents/test_daedalus/test_main.py -v

# Integration tests
pytest tests/integration/ -k daedalus -v
```

## 📊 Session Management

### Vector Memory

Daedalus stores conversations in Qdrant:
- **Collection:** `daedalus_sessions`
- **Vector Dimensions:** 1536 (Azure OpenAI embedding)
- **Metadata:** User ID, session ID, mode, timestamp

### Session Browser

View and restore sessions:

```python
# In chat
/sessions           # View session browser
/resume abc123      # Restore session by ID
```

Session data includes:
- Conversation history
- Agent mode used
- Timestamp
- User context

## 🔐 Security

### Authentication

Supports multiple auth methods:
- Azure AD SSO (recommended)
- Azure AD Hybrid
- Local development (header-based)

Configure in `.env`:
```bash
CHAINLIT_AUTH_SECRET=your_secret_key
OAUTH_AZURE_CLIENT_ID=...
OAUTH_AZURE_CLIENT_SECRET=...
OAUTH_AZURE_TENANT_ID=...
```

### Data Privacy

- Sessions scoped to user ID
- Vector embeddings encrypted at rest
- No PII in embeddings
- Audit logging available

## 🎨 UI Customization

### Theme

Daedalus uses the Pantheon shared theme:
- `public/theme.json` - Color scheme
- `public/custom.css` - Custom styles
- `public/custom.js` - JavaScript enhancements

### Avatar

Agent avatar location:
```
public/avatars/daedalus.png
```

## 📈 Monitoring

### Qdrant Monitor

Built-in collection monitoring:

```python
from core.qdrant_monitor import QdrantMonitor

monitor = QdrantMonitor()
stats = await monitor.get_collection_stats("daedalus_sessions")
```

### Logging

Logs written to `daedalus.log`:

```python
# Configure log level
DAEDALUS_LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

## 🚢 Deployment

### Local Development
```bash
python launcher.py daedalus
```

### Docker
```bash
# Build
docker build -t pantheon-daedalus -f docker/Dockerfile .

# Run
docker run -p 8000:8000 --env-file .env pantheon-daedalus
```

### Azure Container Apps
```bash
# Deploy using Azure CLI
az containerapp up \
  --name daedalus \
  --resource-group pantheon \
  --image pantheon-daedalus:latest \
  --env-vars @.env
```

## 🔄 Updates & Versioning

Version: **1.0.0**

### Changelog
- **1.0.0** - Initial release with Platform and Cloud modes
- Pantheon restructuring
- SSO integration
- Session management

## 🤝 Contributing

See main `CONTRIBUTING.md` for guidelines.

Daedalus-specific:
1. Test both agent modes
2. Update instruction files
3. Maintain backward compatibility
4. Document new features

## 📚 Additional Resources

- [Core Library Documentation](../../core/README.md)
- [Building New Agents Guide](../../docs/BUILDING_NEW_AGENTS.md)
- [Pantheon Architecture](../../docs/architecture/)
- [Azure Well-Architected Framework](https://learn.microsoft.com/azure/well-architected/)

## 🐛 Troubleshooting

### Common Issues

**Issue:** Agent won't start
```bash
# Check environment variables
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('AZURE_OPENAI_API_KEY'))"

# Verify Qdrant connection
curl http://localhost:6333/collections
```

**Issue:** Sessions not saving
```bash
# Check Qdrant collection
curl http://localhost:6333/collections/daedalus_sessions

# Enable debug logging
DAEDALUS_LOG_LEVEL=DEBUG python launcher.py daedalus
```

**Issue:** Mode switching not working
- Verify instruction files exist in `instructions/`
- Check file paths in agent configuration
- Review logs for loading errors

## 📞 Support

For Daedalus-specific issues:
1. Check this README
2. Review agent logs (`daedalus.log`)
3. Check Qdrant collection health
4. Consult core library docs

---

*Daedalus is part of the Pantheon Multi-Agent System* 🏛️

**Agent:** Daedalus  
**Role:** Azure Architecture Assistant  
**Status:** Active  
**Maintainer:** Pantheon Team
