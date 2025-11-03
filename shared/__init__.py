"""
Shared Utilities for Agent Framework

This package contains utilities shared by both agent_core library
and main agent implementations (daedalus.py, agent_sso.py, etc.)

Modules:
- vector_memory: Vector memory manager with Qdrant integration
- qdrant_data_layer: Chainlit data layer for thread history persistence
"""

from .vector_memory import (
    VectorMemoryManager,
    create_vector_memory_manager,
)

from .qdrant_data_layer import (
    QdrantDataLayer,
)

__all__ = [
    "VectorMemoryManager",
    "create_vector_memory_manager",
    "QdrantDataLayer",
]

__version__ = "1.0.0"
