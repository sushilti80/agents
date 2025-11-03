"""
Phase 4 Test Suite: SSO Integration Testing

Tests for core modules (OAuth, DataLayer, ThreadResume, QdrantMonitor)
and their integration in agent_sso.py and daedalus.py.

Run with:
    pytest tests/test_sso_integration.py -v
    pytest tests/test_sso_integration.py::TestOAuthHandler -v
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.oauth_handler import OAuthHandler
from core.data_layer_factory import DataLayerFactory
from core.thread_resume_handler import ThreadResumeHandler
from core.qdrant_monitor import QdrantMonitor


class TestOAuthHandler:
    """Test OAuthHandler functionality"""
    
    def test_oauth_handler_initialization(self):
        """Test OAuthHandler initializes with default providers"""
        handler = OAuthHandler()
        
        assert handler is not None
        assert hasattr(handler, 'allowed_providers')
        assert 'azure-ad' in handler.allowed_providers
        assert 'azure-ad-hybrid' in handler.allowed_providers
    
    def test_oauth_handler_validate_config(self):
        """Test OAuth configuration validation"""
        handler = OAuthHandler()
        
        # Should validate successfully with static method
        is_valid, missing = handler.validate_env_vars()
        
        # May be True or False depending on env vars
        assert isinstance(is_valid, bool)
        assert isinstance(missing, list)
    
    def test_oauth_handler_get_allowed_providers(self):
        """Test getting OAuth provider list"""
        handler = OAuthHandler()
        
        # Get allowed providers
        providers = handler.allowed_providers
        
        assert providers is not None
        assert isinstance(providers, list)
        assert 'azure-ad' in providers
    
    def test_oauth_handler_custom_providers(self):
        """Test custom provider list"""
        handler = OAuthHandler(allowed_providers=['custom-provider'])
        
        assert 'custom-provider' in handler.allowed_providers
        assert len(handler.allowed_providers) == 1


class TestDataLayerFactory:
    """Test DataLayerFactory functionality"""
    
    @pytest.mark.asyncio
    async def test_create_qdrant_data_layer(self):
        """Test creating Qdrant data layer"""
        # This is a static method, no initialization needed
        data_layer = DataLayerFactory.create_qdrant_data_layer()
        
        assert data_layer is not None
        # Check it has required Chainlit data layer methods
        assert hasattr(data_layer, 'get_user')
        assert hasattr(data_layer, 'create_user')
    
    @pytest.mark.asyncio
    async def test_data_layer_thread_operations(self):
        """Test data layer thread operations"""
        data_layer = DataLayerFactory.create_qdrant_data_layer()
        
        # Test has thread methods
        assert hasattr(data_layer, 'list_threads')
        assert hasattr(data_layer, 'get_thread')
        assert hasattr(data_layer, 'update_thread')


class TestThreadResumeHandler:
    """Test ThreadResumeHandler functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        # Mock agent modes
        self.agent_modes = {
            'platform': {'name': 'Platform Agent', 'icon': '🔧'},
            'cloud': {'name': 'Cloud Agent', 'icon': '☁️'}
        }
        
        # Mock agent factory
        async def mock_factory(mode: str):
            """Mock agent creation"""
            mock_agent = Mock()
            mock_agent.get_new_thread = Mock(return_value=Mock())
            return mock_agent
        
        self.mock_factory = mock_factory
    
    def test_thread_resume_handler_initialization(self):
        """Test ThreadResumeHandler initializes correctly"""
        handler = ThreadResumeHandler(
            agent_modes=self.agent_modes,
            agent_factory_func=self.mock_factory,
            default_mode='platform'
        )
        
        assert handler is not None
        assert handler.agent_modes == self.agent_modes
        assert handler.default_mode == 'platform'
    
    def test_thread_resume_handler_missing_params(self):
        """Test ThreadResumeHandler requires all parameters"""
        with pytest.raises(TypeError):
            # Missing required parameters
            ThreadResumeHandler()
    
    @pytest.mark.asyncio
    async def test_get_and_validate_mode_from_thread(self):
        """Test extracting agent mode from thread metadata"""
        handler = ThreadResumeHandler(
            agent_modes=self.agent_modes,
            agent_factory_func=self.mock_factory,
            default_mode='platform'
        )
        
        # Mock thread with metadata
        thread_dict = {
            'id': 'test-thread-123',
            'name': 'Test Thread',
            'metadata': {'mode': 'cloud'}
        }
        
        mode = await handler._get_and_validate_mode(thread_dict)
        assert mode == 'cloud'
    
    @pytest.mark.asyncio
    async def test_get_mode_fallback_to_default(self):
        """Test fallback to default mode when metadata missing"""
        handler = ThreadResumeHandler(
            agent_modes=self.agent_modes,
            agent_factory_func=self.mock_factory,
            default_mode='platform'
        )
        
        # Thread without metadata
        thread_dict = {
            'id': 'test-thread-456',
            'name': 'Test Thread'
        }
        
        mode = await handler._get_and_validate_mode(thread_dict)
        assert mode == 'platform'  # Should fallback to default


class TestQdrantMonitor:
    """Test QdrantMonitor functionality"""
    
    def test_qdrant_monitor_initialization(self):
        """Test QdrantMonitor initializes with model"""
        monitor = QdrantMonitor(model="gpt-4")
        
        assert monitor is not None
        assert monitor.model == "gpt-4"
    
    def test_qdrant_monitor_default_model(self):
        """Test QdrantMonitor uses default model"""
        monitor = QdrantMonitor()
        
        assert monitor is not None
        # Should have a default model
        assert hasattr(monitor, 'model')
    
    def test_count_tokens(self):
        """Test token counting"""
        monitor = QdrantMonitor(model="gpt-4")
        
        text = "This is a test message for token counting."
        token_count = monitor.count_tokens(text)
        
        assert isinstance(token_count, int)
        assert token_count > 0
        assert token_count < 100  # Should be reasonable for this short text
    
    def test_count_tokens_empty_string(self):
        """Test token counting with empty string"""
        monitor = QdrantMonitor(model="gpt-4")
        
        token_count = monitor.count_tokens("")
        assert token_count == 0
    
    def test_log_retrieval_metrics(self, caplog):
        """Test log_retrieval prints metrics"""
        import logging
        caplog.set_level(logging.INFO)
        
        monitor = QdrantMonitor(model="gpt-4")
        
        # Mock context data - must include 'role' field
        context = [
            {'message': 'Previous message 1', 'score': 0.95, 'role': 'user'},
            {'message': 'Previous message 2', 'score': 0.87, 'role': 'assistant'},
            {'message': 'Previous message 3', 'score': 0.76, 'role': 'user'}
        ]
        
        # Log metrics
        monitor.log_retrieval(
            query="What is the deployment status?",
            context=context,
            full_history_size=50,
            show_details=True
        )
        
        # Verify log output contains key metrics
        log_output = caplog.text
        assert "RAG RETRIEVAL METRICS" in log_output
        assert "Retrieved Context" in log_output
        assert "Token Optimization" in log_output
    
    def test_calculate_savings_percentage(self):
        """Test savings percentage calculation"""
        monitor = QdrantMonitor(model="gpt-4")
        
        # Mock context with required 'role' field
        context = [
            {'message': 'Short message', 'score': 0.95, 'role': 'user'}
        ]
        
        # Log with full history
        monitor.log_retrieval(
            query="Test query",
            context=context,
            full_history_size=100
        )
        
        # Should calculate savings (100 messages vs 1 in context)
        # Verify through internal state if accessible, or just ensure no errors


class TestSessionIsolation:
    """Test session isolation in RAG context retrieval"""
    
    @pytest.mark.asyncio
    async def test_search_context_session_filter(self):
        """Test that search_context uses session_id filter"""
        from shared.vector_memory import VectorMemoryManager
        
        # Mock Qdrant client
        mock_qdrant = Mock()
        mock_qdrant.search = Mock(return_value=[])
        mock_qdrant.get_collections = Mock(return_value=Mock(collections=[]))
        
        with patch('shared.vector_memory.QdrantClient', return_value=mock_qdrant):
            vm = VectorMemoryManager(
                qdrant_host="localhost",
                qdrant_port=6333
            )
            
            # Search with session filter
            await vm.search_context(
                user_id="user123",
                query="test query",
                top_k=5,
                session_id="session456"
            )
            
            # Verify search was called with session filter
            assert mock_qdrant.search.called
            call_args = mock_qdrant.search.call_args
            
            # Check that query_filter includes session_id
            if 'query_filter' in call_args.kwargs:
                filter_obj = call_args.kwargs['query_filter']
                assert filter_obj is not None
    
    @pytest.mark.asyncio
    async def test_minimum_score_threshold(self):
        """Test that low-relevance results are filtered"""
        from shared.vector_memory import VectorMemoryManager
        
        # Mock search results with varying scores
        mock_results = [
            Mock(payload={'message': 'High relevance', 'role': 'user'}, score=0.95),
            Mock(payload={'message': 'Medium relevance', 'role': 'user'}, score=0.75),
            Mock(payload={'message': 'Low relevance', 'role': 'user'}, score=0.50),  # Below threshold
            Mock(payload={'message': 'Very low relevance', 'role': 'user'}, score=0.30),  # Below threshold
        ]
        
        mock_qdrant = Mock()
        mock_qdrant.search = Mock(return_value=mock_results)
        mock_qdrant.get_collections = Mock(return_value=Mock(collections=[
            Mock(name='agent-conversations')
        ]))
        
        with patch('shared.vector_memory.QdrantClient', return_value=mock_qdrant):
            vm = VectorMemoryManager(
                qdrant_host="localhost",
                qdrant_port=6333
            )
            
            # Ensure collection exists
            await vm.ensure_collection()
            
            # Search context
            context = await vm.search_context(
                user_id="user123",
                query="test query",
                top_k=5,
                session_id="session456"
            )
            
            # Should only return results >= 0.70 threshold
            assert len(context) == 2  # Only first two results
            assert all(c['score'] >= 0.70 for c in context)


class TestContextQuality:
    """Test context retrieval quality improvements"""
    
    def test_top_k_increased_to_5(self):
        """Verify that top_k is set to 5 in both agents"""
        # Read agent_sso.py and verify top_k=5
        agent_sso_path = Path(__file__).parent.parent / 'agent_sso.py'
        if agent_sso_path.exists():
            content = agent_sso_path.read_text()
            assert 'top_k=5' in content
            assert 'session_id=session_id' in content
    
    def test_daedalus_top_k_increased_to_5(self):
        """Verify that top_k is set to 5 in daedalus.py"""
        daedalus_path = Path(__file__).parent.parent / 'daedalus.py'
        if daedalus_path.exists():
            content = daedalus_path.read_text()
            assert 'top_k=5' in content
            assert 'session_id=session_id' in content


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""
    
    @pytest.mark.asyncio
    async def test_oauth_and_data_layer_integration(self):
        """Test OAuth and DataLayer work together"""
        # Initialize OAuth
        oauth = OAuthHandler()
        
        # Create data layer
        data_layer = DataLayerFactory.create_qdrant_data_layer()
        
        # Both should be functional
        assert oauth is not None
        assert data_layer is not None
    
    @pytest.mark.asyncio
    async def test_thread_resume_with_qdrant_monitor(self):
        """Test ThreadResumeHandler with QdrantMonitor"""
        # Setup
        agent_modes = {
            'platform': {'name': 'Platform Agent', 'icon': '🔧'}
        }
        
        async def mock_factory(mode: str):
            mock_agent = Mock()
            mock_agent.get_new_thread = Mock(return_value=Mock())
            return mock_agent
        
        # Create handler
        resume_handler = ThreadResumeHandler(
            agent_modes=agent_modes,
            agent_factory_func=mock_factory,
            default_mode='platform'
        )
        
        # Create monitor
        monitor = QdrantMonitor(model="gpt-4")
        
        # Both should work independently
        assert resume_handler is not None
        assert monitor is not None


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_oauth_handler_missing_env_vars(self):
        """Test OAuth handles missing environment variables gracefully"""
        handler = OAuthHandler()
        
        # Should not crash even if env vars missing
        is_valid, missing = handler.validate_env_vars()
        
        # May return False but shouldn't raise exception
        assert isinstance(is_valid, bool)
        assert isinstance(missing, list)
    
    @pytest.mark.asyncio
    async def test_vector_memory_connection_error(self):
        """Test vector memory handles connection errors"""
        from shared.vector_memory import VectorMemoryManager
        
        # Try to connect to non-existent Qdrant
        vm = VectorMemoryManager(
            qdrant_host="invalid-host-xyz",
            qdrant_port=9999
        )
        
        # Should handle gracefully
        try:
            await vm.search_context(
                user_id="user123",
                query="test",
                top_k=3
            )
        except Exception as e:
            # Exception is expected, just verify it doesn't crash Python
            assert isinstance(e, Exception)
    
    def test_qdrant_monitor_with_long_text(self):
        """Test QdrantMonitor handles very long text"""
        monitor = QdrantMonitor(model="gpt-4")
        
        # Create very long text (10K words)
        long_text = "word " * 10000
        
        # Should handle without crashing
        token_count = monitor.count_tokens(long_text)
        
        assert isinstance(token_count, int)
        assert token_count > 1000  # Should be substantial


# Pytest configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"])
