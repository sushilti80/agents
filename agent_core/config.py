"""
Configuration classes and constants for agent core library
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AgentMode:
    """Agent mode configuration"""
    name: str
    file: str
    emoji: str
    description: str


@dataclass
class SessionConfig:
    """Session management configuration"""
    max_sessions_query: int = 100
    max_sessions_display: int = 10
    max_history_messages: int = 100
    session_id_prefix: str = "session_"
    short_id_length: int = 8


@dataclass
class CommandConfig:
    """Command configuration"""
    debug: List[str] = field(default_factory=lambda: ["/debug", "/debug-sessions"])
    list_sessions: List[str] = field(default_factory=lambda: ["/sessions", "/list"])
    session_info: str = "/session"
    resume: str = "/resume"
    help: str = "/help"


@dataclass
class AgentConfig:
    """Main agent configuration"""
    agent_name: str = "Agent"
    agent_modes: Dict[str, AgentMode] = field(default_factory=dict)
    default_mode: str = "default"
    session_config: SessionConfig = field(default_factory=SessionConfig)
    command_config: CommandConfig = field(default_factory=CommandConfig)
    instruction_base_dir: str = "."
    log_file: str = "agent.log"
    log_level: str = "INFO"
    temperature: float = 0.2
    
    # Azure OpenAI Configuration - environment variable names to try in order
    azure_openai_deployment: List[str] = field(default_factory=lambda: [
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME",
        "AZURE_OPENAI_MODEL",
        "OPENAI_DEPLOYMENT"
    ])
    azure_openai_endpoint: List[str] = field(default_factory=lambda: [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_BASE_URL",
        "AZURE_OPENAI_URL",
        "OPENAI_ENDPOINT"
    ])
    azure_openai_api_key: List[str] = field(default_factory=lambda: [
        "AZURE_OPENAI_API_KEY",
        "OPENAI_API_KEY",
        "AOAI_API_KEY"
    ])
    azure_openai_api_version: List[str] = field(default_factory=lambda: [
        "AZURE_OPENAI_API_VERSION",
        "OPENAI_API_VERSION"
    ])
    default_api_version: str = "2024-05-01-preview"


# Default configuration instances
DEFAULT_SESSION_CONFIG = SessionConfig()
DEFAULT_COMMAND_CONFIG = CommandConfig()
DEFAULT_AGENT_CONFIG = AgentConfig()
