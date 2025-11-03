"""
Agent factory and creation utilities
Handles agent initialization, chat client creation, and instruction loading
"""
import os
import logging
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import asdict

from agent_framework import ChatAgent, MCPStdioTool, MCPStreamableHTTPTool
from agent_framework.azure import AzureOpenAIChatClient

from .config import AgentConfig, AgentMode, DEFAULT_AGENT_CONFIG
from .utils import get_env_with_fallback, load_instruction_file

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for creating and configuring agents"""
    
    def __init__(self, config: AgentConfig = None):
        """
        Initialize AgentFactory.
        
        Args:
            config: Agent configuration (uses defaults if not provided)
        """
        self.config = config or DEFAULT_AGENT_CONFIG
    
    def create_chat_client(self) -> AzureOpenAIChatClient:
        """
        Create Azure OpenAI chat client with environment configuration.
        
        Returns:
            Configured AzureOpenAIChatClient instance
        
        Raises:
            ValueError: If required environment variables are missing
        """
        # Get Azure OpenAI configuration from environment
        api_key = get_env_with_fallback(
            self.config.azure_openai_api_key[0],
            self.config.azure_openai_api_key[1:]
        )
        
        endpoint = get_env_with_fallback(
            self.config.azure_openai_endpoint[0],
            self.config.azure_openai_endpoint[1:]
        )
        
        deployment_name = get_env_with_fallback(
            self.config.azure_openai_deployment[0],
            self.config.azure_openai_deployment[1:]
        )
        
        api_version = get_env_with_fallback(
            self.config.azure_openai_api_version[0],
            self.config.azure_openai_api_version[1:]
        ) or self.config.default_api_version
        
        # Validate required configuration
        if not all([api_key, endpoint, deployment_name]):
            raise ValueError(
                "Missing required Azure OpenAI configuration. "
                "Please set AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT_NAME"
            )
        
        logger.info(f"Creating Azure OpenAI client for deployment: {deployment_name}")
        
        return AzureOpenAIChatClient(
            deployment_name=deployment_name,
            endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
    
    def load_mode_instructions(
        self, 
        mode: AgentMode,
        base_dir: Optional[str] = None
    ) -> str:
        """
        Load instruction file for a specific mode.
        
        Args:
            mode: AgentMode to load instructions for
            base_dir: Base directory for instruction files (uses config if not provided)
        
        Returns:
            Instruction text content
        """
        base = Path(base_dir) if base_dir else Path(self.config.instruction_base_dir)
        return load_instruction_file(mode.file, base)
    
    def setup_mcp_tools(self) -> List:
        """
        Setup MCP (Model Context Protocol) tools.
        
        Returns:
            List of configured MCP tool instances
        """
        mcp_tools = []
        
        try:
            # Sequential Thinking MCP (stdio)
            sequential_thinking = MCPStdioTool(
                name="sequential-thinking",
                command="mcp-server-sequential-thinking",
                description="Advanced reasoning tool for complex problem-solving with step-by-step thinking",
                load_prompts=False
            )
            mcp_tools.append(sequential_thinking)
            logger.info("Added Sequential Thinking MCP tool")
            
        except Exception as e:
            logger.warning(f"Failed to setup Sequential Thinking MCP: {e}")
        
        try:
            # Microsoft Learn MCP (HTTP)
            microsoft_learn = MCPStreamableHTTPTool(
                name="Microsoft Learn MCP",
                url="https://learn.microsoft.com/api/mcp",
                description="Search and retrieve official Microsoft/Azure documentation, code samples, and best practices",
                load_prompts=False
            )
            mcp_tools.append(microsoft_learn)
            logger.info("Added Microsoft Learn MCP tool")
            
        except Exception as e:
            logger.warning(f"Failed to setup Microsoft Learn MCP: {e}")
        
        return mcp_tools
    
    async def create_agent(
        self,
        mode_name: Optional[str] = None,
        custom_instructions: Optional[str] = None
    ) -> ChatAgent:
        """
        Create a configured ChatAgent instance.
        
        Args:
            mode_name: Agent mode to use (uses default if not provided)
            custom_instructions: Custom instruction text (overrides mode file)
        
        Returns:
            Configured ChatAgent instance
        """
        # Determine mode
        mode_name = mode_name or self.config.default_mode
        mode = self.config.agent_modes.get(mode_name)
        
        if not mode:
            logger.warning(f"Mode {mode_name} not found, using default {self.config.default_mode}")
            mode = self.config.agent_modes[self.config.default_mode]
        
        # Load instructions
        if custom_instructions:
            instructions = custom_instructions
        else:
            instructions = self.load_mode_instructions(mode)
        
        # Create chat client
        chat_client = self.create_chat_client()
        
        # Setup MCP tools
        mcp_tools = self.setup_mcp_tools()
        
        # Create agent
        logger.info(f"Creating agent in {mode.name} mode")
        agent = ChatAgent(
            name=self.config.agent_name.replace(" ", ""),
            chat_client=chat_client,
            instructions=instructions,
            tools=mcp_tools,
            temperature=self.config.temperature
        )
        
        return agent


# Standalone functions for backward compatibility
def create_chat_client(
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    deployment: Optional[str] = None,
    api_version: Optional[str] = None,
    temperature: float = 0.2
) -> AzureOpenAIChatClient:
    """
    Create Azure OpenAI chat client.
    
    If parameters are not provided, uses environment variables.
    """
    if not all([api_key, endpoint, deployment]):
        factory = AgentFactory()
        return factory.create_chat_client()
    
    return AzureOpenAIChatClient(
        api_key=api_key,
        azure_endpoint=endpoint,
        azure_deployment=deployment,
        api_version=api_version or "2024-02-15-preview",
        temperature=temperature
    )


def load_instructions(
    file_path: str,
    base_dir: Optional[str] = None
) -> str:
    """Load instruction file"""
    return load_instruction_file(file_path, base_dir)


async def create_agent(
    mode_name: str = "azure",
    custom_instructions: Optional[str] = None,
    config: Optional[AgentConfig] = None
) -> ChatAgent:
    """Create a configured agent"""
    factory = AgentFactory(config)
    return await factory.create_agent(mode_name, custom_instructions)
