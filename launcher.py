#!/usr/bin/env python3
"""
Pantheon - Multi-Agent Launcher

Launch any agent in the Pantheon system with customized settings.

Usage:
    python launcher.py daedalus                  # Launch Daedalus agent
    python launcher.py daedalus --mode platform  # Launch with specific mode
    python launcher.py --list                     # List available agents
    python launcher.py --help                     # Show help
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Optional
import argparse

# Available agents configuration
AGENTS = {
    "daedalus": {
        "name": "Daedalus",
        "description": "Azure Architecture Assistant",
        "emoji": "🏗️",
        "path": "agents/daedalus/main.py",
        "modes": ["platform", "cloud"],
        "default_mode": "platform",
        "port": 8000
    },
    # Future agents can be added here
    # "security": {
    #     "name": "Security Sentinel",
    #     "description": "Cloud Security Advisor",
    #     "emoji": "🛡️",
    #     "path": "agents/security/main.py",
    #     "modes": ["compliance", "threat"],
    #     "default_mode": "compliance",
    #     "port": 8001
    # },
}


def list_agents():
    """Display all available agents"""
    print("\n🏛️  Pantheon - Available Agents\n")
    print("=" * 60)
    
    if not AGENTS:
        print("No agents available.")
        return
    
    for agent_id, config in AGENTS.items():
        print(f"\n{config['emoji']} {config['name']}")
        print(f"   ID: {agent_id}")
        print(f"   Description: {config['description']}")
        print(f"   Available modes: {', '.join(config['modes'])}")
        print(f"   Default port: {config['port']}")
    
    print("\n" + "=" * 60)
    print("\nUsage:")
    print(f"  python launcher.py <agent_id>")
    print(f"  python launcher.py daedalus --mode platform")
    print()


def launch_agent(
    agent_id: str,
    mode: Optional[str] = None,
    port: Optional[int] = None,
    watch: bool = True
):
    """
    Launch a specific agent
    
    Args:
        agent_id: ID of the agent to launch
        mode: Optional agent mode to start with
        port: Optional port override
        watch: Enable auto-reload on file changes
    """
    if agent_id not in AGENTS:
        print(f"❌ Agent '{agent_id}' not found.")
        print(f"\nAvailable agents: {', '.join(AGENTS.keys())}")
        print(f"\nRun 'python launcher.py --list' to see all agents.")
        sys.exit(1)
    
    config = AGENTS[agent_id]
    agent_path = Path(config["path"])
    
    # Validate agent file exists
    if not agent_path.exists():
        print(f"❌ Agent file not found: {agent_path}")
        sys.exit(1)
    
    # Validate mode if specified
    if mode and mode not in config["modes"]:
        print(f"❌ Invalid mode '{mode}' for {config['name']}")
        print(f"   Available modes: {', '.join(config['modes'])}")
        sys.exit(1)
    
    # Build launch command
    launch_port = port or config["port"]
    
    print(f"\n🏛️  Pantheon Launcher")
    print("=" * 60)
    print(f"{config['emoji']} Launching: {config['name']}")
    print(f"   Description: {config['description']}")
    print(f"   Mode: {mode or config['default_mode']} (default)" if not mode else f"   Mode: {mode}")
    print(f"   Port: {launch_port}")
    print(f"   File: {agent_path}")
    print("=" * 60)
    print()
    
    # Build chainlit command
    cmd = ["chainlit", "run", str(agent_path)]
    
    if watch:
        cmd.append("-w")
    
    if port:
        cmd.extend(["--port", str(port)])
    
    # Set environment variable for mode if specified
    env = None
    if mode:
        import os
        env = os.environ.copy()
        env["AGENT_DEFAULT_MODE"] = mode
    
    try:
        # Launch the agent
        subprocess.run(cmd, env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error launching agent: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n\n{config['emoji']} {config['name']} stopped.")
        sys.exit(0)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="🏛️  Pantheon - Multi-Agent Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launcher.py daedalus                  Launch Daedalus agent
  python launcher.py daedalus --mode platform  Launch with specific mode
  python launcher.py daedalus --port 8080      Launch on custom port
  python launcher.py --list                     List all available agents
        """
    )
    
    parser.add_argument(
        "agent",
        nargs="?",
        help="Agent ID to launch (e.g., daedalus)"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available agents"
    )
    
    parser.add_argument(
        "--mode",
        type=str,
        help="Agent mode to start with"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        help="Port to run the agent on (overrides default)"
    )
    
    parser.add_argument(
        "--no-watch",
        action="store_true",
        help="Disable auto-reload on file changes"
    )
    
    args = parser.parse_args()
    
    # Handle --list flag
    if args.list:
        list_agents()
        sys.exit(0)
    
    # Require agent ID if not listing
    if not args.agent:
        parser.print_help()
        print("\n" + "=" * 60)
        list_agents()
        sys.exit(1)
    
    # Launch the agent
    launch_agent(
        agent_id=args.agent,
        mode=args.mode,
        port=args.port,
        watch=not args.no_watch
    )


if __name__ == "__main__":
    main()
