"""
Utility functions for agent core library
"""
import os
import logging
from typing import Optional, List
from pathlib import Path


def get_env_with_fallback(primary: str, fallbacks: List[str]) -> Optional[str]:
    """
    Return first non-empty environment variable value among primary then fallbacks.
    
    Args:
        primary: Primary environment variable name
        fallbacks: List of fallback environment variable names
    
    Returns:
        str: First non-empty value found, or None
    """
    val = os.getenv(primary)
    if val:
        return val
    
    for name in fallbacks:
        v = os.getenv(name)
        if v:
            logging.info(f"Using fallback env var '{name}' for '{primary}'.")
            return v
    
    return None


def setup_logging(log_file: str = "agent.log", log_level: str = "INFO") -> logging.Logger:
    """
    Configure logging for the agent.
    
    Args:
        log_file: Path to log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def load_instruction_file(file_path: str, base_dir: Optional[Path] = None) -> str:
    """
    Load instruction text from a file.
    
    Args:
        file_path: Relative or absolute path to instruction file
        base_dir: Base directory for relative paths (defaults to current file's parent)
    
    Returns:
        str: Instruction text content
    
    Raises:
        FileNotFoundError: If instruction file doesn't exist
    """
    if base_dir is None:
        base_dir = Path.cwd()
    
    instructions_path = base_dir / file_path if not Path(file_path).is_absolute() else Path(file_path)
    
    if not instructions_path.exists():
        raise FileNotFoundError(f"Instruction file not found: {instructions_path}")
    
    return instructions_path.read_text(encoding="utf-8")


def format_session_id(session_id: str, prefix: str = "session_") -> str:
    """
    Ensure session ID has proper prefix.
    
    Args:
        session_id: Session ID to format
        prefix: Prefix to ensure (default: "session_")
    
    Returns:
        str: Formatted session ID
    """
    return session_id if session_id.startswith(prefix) else f"{prefix}{session_id}"


def extract_short_id(session_id: str, length: int = 8) -> str:
    """
    Extract short readable ID from full session ID.
    
    Args:
        session_id: Full session ID
        length: Length of short ID to extract
    
    Returns:
        str: Short session ID
    """
    return session_id.split("_")[-1][:length] if "_" in session_id else session_id[:length]


def get_mode_emoji(mode: str, mode_emojis: dict) -> str:
    """
    Get emoji for agent mode.
    
    Args:
        mode: Mode identifier
        mode_emojis: Dict mapping mode to emoji
    
    Returns:
        str: Emoji for mode, or empty string if not found
    """
    return mode_emojis.get(mode, "")
