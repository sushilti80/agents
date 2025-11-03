"""
Data Layer Factory for Chainlit Applications
Creates and configures data layers for thread history persistence
"""
import logging
from typing import Optional
from chainlit.data import BaseDataLayer

logger = logging.getLogger(__name__)


class DataLayerFactory:
    """
    Factory for creating Chainlit data layers.
    Supports Qdrant vector storage integration out of the box.
    
    Usage:
        @cl.data_layer
        def get_data_layer():
            return DataLayerFactory.create_qdrant_data_layer()
    """
    
    @staticmethod
    def create_qdrant_data_layer() -> BaseDataLayer:
        """
        Create and initialize a Qdrant-backed data layer.
        
        This integrates Qdrant vector storage with Chainlit's thread history UI,
        enabling the native left sidebar to display conversation threads.
        
        Returns:
            QdrantDataLayer instance ready for use
        
        Raises:
            ImportError: If qdrant_data_layer or vector_memory modules are missing
            Exception: If initialization fails
        
        Example:
            @cl.data_layer
            def get_data_layer():
                return DataLayerFactory.create_qdrant_data_layer()
        """
        try:
            logger.info("🔧 Initializing QdrantDataLayer for thread history sidebar...")
            
            # Import from shared utilities package
            try:
                from shared.qdrant_data_layer import QdrantDataLayer
                from shared.vector_memory import create_vector_memory_manager
            except ImportError:
                # Fallback: try adding parent directory to path
                import sys
                from pathlib import Path
                
                parent_dir = Path(__file__).parent.parent
                if str(parent_dir) not in sys.path:
                    sys.path.insert(0, str(parent_dir))
                
                # Try import again with shared prefix
                from shared.qdrant_data_layer import QdrantDataLayer
                from shared.vector_memory import create_vector_memory_manager
            
            # Create vector memory manager
            vector_memory = create_vector_memory_manager()
            
            # Create data layer
            data_layer = QdrantDataLayer(vector_memory)
            
            logger.info("✅ QdrantDataLayer registered successfully!")
            logger.info("✅ Thread history sidebar should now be enabled")
            
            return data_layer
            
        except ImportError as e:
            # Re-raise import errors with clear message
            logger.error(f"❌ Missing required dependencies: {e}")
            logger.error("⚠️  Ensure 'shared/qdrant_data_layer.py' and 'shared/vector_memory.py' exist")
            raise ImportError(
                f"Failed to import Qdrant dependencies: {e}\n"
                "Please ensure:\n"
                "1. shared/qdrant_data_layer.py exists in the agent directory\n"
                "2. shared/vector_memory.py exists in the agent directory\n"
                "3. qdrant-client is installed: pip install qdrant-client"
            ) from e
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize QdrantDataLayer: {e}", exc_info=True)
            logger.warning("⚠️  Thread history sidebar will NOT be available")
            logger.warning("⚠️  Users will still be able to chat, but won't see past conversations in sidebar")
            raise RuntimeError(
                f"QdrantDataLayer initialization failed: {e}\n"
                "Check Qdrant connection and configuration."
            ) from e
    
    @staticmethod
    def create_null_data_layer() -> BaseDataLayer:
        """
        Create a null/no-op data layer for testing or when persistence is not needed.
        
        This returns None, which disables the data layer functionality in Chainlit.
        Thread history will not be persisted or displayed.
        
        Returns:
            None
        
        Example:
            @cl.data_layer
            def get_data_layer():
                return DataLayerFactory.create_null_data_layer()
        """
        logger.warning("⚠️  Using null data layer - thread history disabled")
        return None


def create_data_layer_decorator(data_layer_type: str = "qdrant"):
    """
    Create a data layer registration function for @cl.data_layer decorator.
    
    This is a convenience function that returns a callable suitable for use
    with Chainlit's @cl.data_layer decorator.
    
    Args:
        data_layer_type: Type of data layer to create.
                        Options: "qdrant", "null"
                        Default: "qdrant"
    
    Returns:
        Function that returns a data layer instance
    
    Raises:
        ValueError: If data_layer_type is unknown
    
    Example:
        # Simple usage
        get_data_layer = create_data_layer_decorator("qdrant")
        
        @cl.data_layer
        def register_data_layer():
            return get_data_layer()
    """
    factory = DataLayerFactory()
    
    def get_data_layer():
        if data_layer_type == "qdrant":
            return factory.create_qdrant_data_layer()
        elif data_layer_type == "null":
            return factory.create_null_data_layer()
        else:
            raise ValueError(
                f"Unknown data layer type: '{data_layer_type}'\n"
                f"Valid options: 'qdrant', 'null'"
            )
    
    return get_data_layer


def register_qdrant_data_layer():
    """
    Convenience function to get a Qdrant data layer.
    
    Use this directly with @cl.data_layer decorator:
    
    Example:
        from agent_core.data_layer_factory import register_qdrant_data_layer
        
        @cl.data_layer
        def get_data_layer():
            return register_qdrant_data_layer()
    """
    return DataLayerFactory.create_qdrant_data_layer()
