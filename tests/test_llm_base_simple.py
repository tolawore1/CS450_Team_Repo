"""Simple tests for llm_base.py"""

import pytest
from unittest.mock import Mock, patch
from ai_model_catalog.metrics.llm_base import LLMEnhancedMetric


class ConcreteLLMEnhancedMetric(LLMEnhancedMetric):
    """Concrete implementation for testing."""
    
    def score_with_llm(self, data):
        """Mock LLM scoring."""
        return 0.8
    
    def score_without_llm(self, data):
        """Mock traditional scoring."""
        return 0.6


def test_init():
    """Test initialization."""
    with patch('ai_model_catalog.metrics.llm_base.get_llm_service') as mock_get_service:
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        metric = ConcreteLLMEnhancedMetric()
        
        assert metric.llm_service == mock_service


def test_score_with_llm_success():
    """Test scoring with successful LLM analysis."""
    metric = ConcreteLLMEnhancedMetric()
    data = {}
    
    result = metric.score(data)
    assert result == 0.8


def test_score_with_llm_error():
    """Test scoring when LLM raises error."""
    class ErrorLLMMetric(LLMEnhancedMetric):
        def score_with_llm(self, data):
            raise ValueError("LLM error")
        
        def score_without_llm(self, data):
            return 0.5
    
    metric = ErrorLLMMetric()
    data = {}
    
    result = metric.score(data)
    assert result == 0.5
