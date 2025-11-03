"""
Qdrant RAG Monitoring Utility

This module provides detailed monitoring and logging for Qdrant vector memory usage,
showing token optimization and context enhancement benefits.

Version: 1.0.0
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import tiktoken

logger = logging.getLogger(__name__)


@dataclass
class RAGMetrics:
    """Metrics for RAG context retrieval and token usage."""
    query_tokens: int
    context_tokens: int
    total_tokens: int
    items_retrieved: int
    avg_relevance_score: float
    token_savings_estimate: int  # Tokens saved vs full history
    

class QdrantMonitor:
    """
    Monitor and log Qdrant RAG operations with detailed metrics.
    
    Features:
    - Token counting for queries and retrieved context
    - Relevance score tracking
    - Token optimization metrics
    - Detailed logging with visual indicators
    """
    
    def __init__(self, model: str = "gpt-4"):
        """
        Initialize the Qdrant monitor.
        
        IMPORTANT: This does NOT call the actual model or make API requests!
        It only loads the local tokenizer for accurate token counting.
        
        Args:
            model: Model name for selecting the correct tokenizer (default: gpt-4)
                   Common values:
                   - "gpt-4" or "gpt-4-turbo" → uses cl100k_base encoding
                   - "gpt-3.5-turbo" → uses cl100k_base encoding
                   - "gpt-4o" → uses o200k_base encoding
                   
                   This is only used to select which tokenizer algorithm to use
                   locally - no API calls are made.
        """
        self.model = model
        try:
            # Load the appropriate tokenizer (runs locally, no API call)
            self.encoding = tiktoken.encoding_for_model(model)
            logger.debug(f"Using tokenizer for model: {model}")
        except KeyError:
            # Fallback to most common encoding if model not recognized
            logger.warning(f"Model {model} not found, using cl100k_base encoding")
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in a text string using local tokenizer.
        
        NOTE: This runs entirely locally - no API calls to Azure/OpenAI!
        
        Args:
            text: Input text
            
        Returns:
            Number of tokens this text would use with the configured tokenizer
        """
        try:
            # Tokenize locally (no network call)
            return len(self.encoding.encode(text))
        except Exception as e:
            logger.error(f"Failed to count tokens: {e}")
            # Rough estimate: 1 token ~= 4 characters
            return len(text) // 4
    
    def calculate_metrics(
        self,
        query: str,
        context: List[Dict],
        full_history_size: int = 0
    ) -> RAGMetrics:
        """
        Calculate comprehensive RAG metrics.
        
        Args:
            query: User query text
            context: Retrieved context items from Qdrant
            full_history_size: Number of messages in full session history
            
        Returns:
            RAGMetrics object with detailed metrics
        """
        query_tokens = self.count_tokens(query)
        
        # Calculate context tokens
        context_text = ""
        for item in context:
            context_text += f"{item['message']}\n"
        context_tokens = self.count_tokens(context_text)
        
        total_tokens = query_tokens + context_tokens
        
        # Calculate average relevance score
        avg_score = 0.0
        if context:
            avg_score = sum(item.get('score', 0.0) for item in context) / len(context)
        
        # Estimate token savings
        # Assume full history would be ~200 tokens per message
        estimated_full_history_tokens = full_history_size * 200
        token_savings = max(0, estimated_full_history_tokens - context_tokens)
        
        return RAGMetrics(
            query_tokens=query_tokens,
            context_tokens=context_tokens,
            total_tokens=total_tokens,
            items_retrieved=len(context),
            avg_relevance_score=avg_score,
            token_savings_estimate=token_savings
        )
    
    def log_retrieval(
        self,
        query: str,
        context: List[Dict],
        full_history_size: int = 0,
        show_details: bool = True
    ):
        """
        Log detailed RAG retrieval metrics with visual formatting.
        
        Args:
            query: User query text
            context: Retrieved context items
            full_history_size: Size of full conversation history
            show_details: Whether to show detailed context items
        """
        metrics = self.calculate_metrics(query, context, full_history_size)
        
        # Visual separator
        logger.info("=" * 80)
        logger.info("📊 QDRANT RAG RETRIEVAL METRICS")
        logger.info("=" * 80)
        
        # Query info
        logger.info(f"🔍 Query: '{query[:100]}{'...' if len(query) > 100 else ''}'")
        logger.info(f"   Tokens: {metrics.query_tokens}")
        
        # Context retrieval
        logger.info(f"\n📦 Retrieved Context:")
        logger.info(f"   Items Retrieved: {metrics.items_retrieved}")
        logger.info(f"   Context Tokens: {metrics.context_tokens}")
        logger.info(f"   Avg Relevance Score: {metrics.avg_relevance_score:.4f}")
        
        # Token optimization
        logger.info(f"\n💰 Token Optimization:")
        logger.info(f"   Total Prompt Tokens: {metrics.total_tokens}")
        if full_history_size > 0:
            logger.info(f"   Full History Messages: {full_history_size}")
            logger.info(f"   Estimated Token Savings: {metrics.token_savings_estimate} tokens")
            savings_percent = (metrics.token_savings_estimate / (metrics.token_savings_estimate + metrics.context_tokens)) * 100 if metrics.token_savings_estimate > 0 else 0
            logger.info(f"   Savings Percentage: {savings_percent:.1f}%")
        
        # Detailed context items
        if show_details and context:
            logger.info(f"\n🔎 Retrieved Context Details:")
            for i, item in enumerate(context, 1):
                role_icon = "👤" if item["role"] == "user" else "🤖"
                logger.info(f"   {i}. {role_icon} [Score: {item.get('score', 0):.4f}]")
                message_preview = item['message'][:150]
                if len(item['message']) > 150:
                    message_preview += "..."
                logger.info(f"      {message_preview}")
                if item.get('timestamp'):
                    logger.info(f"      Timestamp: {item['timestamp']}")
        
        logger.info("=" * 80)
    
    def log_storage(self, user_id: str, message: str, role: str):
        """
        Log message storage to Qdrant.
        
        Args:
            user_id: User identifier
            message: Message content
            role: Message role (user/assistant)
        """
        tokens = self.count_tokens(message)
        role_icon = "👤" if role == "user" else "🤖"
        
        logger.info(f"💾 Storing in Qdrant: {role_icon} {role.upper()}")
        logger.info(f"   User: {user_id}")
        logger.info(f"   Tokens: {tokens}")
        logger.info(f"   Preview: {message[:100]}{'...' if len(message) > 100 else ''}")
    
    def create_summary_report(self, sessions_metrics: List[RAGMetrics]) -> str:
        """
        Create a summary report of RAG performance across sessions.
        
        Args:
            sessions_metrics: List of RAGMetrics from multiple sessions
            
        Returns:
            Formatted summary report
        """
        if not sessions_metrics:
            return "No metrics available"
        
        total_retrievals = len(sessions_metrics)
        avg_context_tokens = sum(m.context_tokens for m in sessions_metrics) / total_retrievals
        avg_items = sum(m.items_retrieved for m in sessions_metrics) / total_retrievals
        avg_relevance = sum(m.avg_relevance_score for m in sessions_metrics) / total_retrievals
        total_savings = sum(m.token_savings_estimate for m in sessions_metrics)
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║           QDRANT RAG PERFORMANCE SUMMARY                         ║
╚══════════════════════════════════════════════════════════════════╝

📈 Overall Statistics:
   • Total Retrievals: {total_retrievals}
   • Avg Context Tokens/Query: {avg_context_tokens:.1f}
   • Avg Items Retrieved: {avg_items:.1f}
   • Avg Relevance Score: {avg_relevance:.4f}
   
💰 Token Optimization:
   • Total Tokens Saved: {total_savings:,}
   • Avg Savings/Query: {total_savings/total_retrievals:.1f}

🎯 RAG Effectiveness:
   {"✅ Excellent" if avg_relevance > 0.8 else "⚠️ Good" if avg_relevance > 0.6 else "❌ Needs Tuning"}
   (Relevance threshold: >0.8 excellent, >0.6 good)
        """
        
        return report


# Example usage functions

async def monitor_rag_retrieval(
    vector_memory,
    user_id: str,
    query: str,
    top_k: int = 3,
    show_details: bool = True
) -> List[Dict]:
    """
    Helper function to retrieve context with monitoring.
    
    Args:
        vector_memory: VectorMemoryManager instance
        user_id: User identifier
        query: Search query
        top_k: Number of results
        show_details: Show detailed logs
        
    Returns:
        Retrieved context items
    """
    monitor = QdrantMonitor()
    
    # Retrieve context
    context = await vector_memory.search_context(
        user_id=user_id,
        query=query,
        top_k=top_k
    )
    
    # Get full history size for comparison
    full_history = await vector_memory.get_session_history(
        user_id=user_id,
        session_id=vector_memory.collection_name,  # or actual session_id
        limit=100
    )
    
    # Log metrics
    monitor.log_retrieval(
        query=query,
        context=context,
        full_history_size=len(full_history),
        show_details=show_details
    )
    
    return context


def create_qdrant_monitor(model: str = "gpt-4") -> QdrantMonitor:
    """
    Factory function to create a QdrantMonitor instance.
    
    Args:
        model: Model name for token counting
        
    Returns:
        QdrantMonitor instance
    """
    return QdrantMonitor(model=model)
