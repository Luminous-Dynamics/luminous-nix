"""
Tests for the knowledge engine module.
"""

import pytest
from unittest.mock import Mock, patch
import json

def test_knowledge_engine_init():
    """Test knowledge engine initialization."""
    from luminous_nix.knowledge.engine import ModernNixOSKnowledgeEngine
    
    engine = ModernNixOSKnowledgeEngine()
    assert engine is not None
    assert hasattr(engine, 'query')
    assert hasattr(engine, 'search')


def test_knowledge_query():
    """Test knowledge queries."""
    from luminous_nix.knowledge.engine import ModernNixOSKnowledgeEngine
    
    engine = ModernNixOSKnowledgeEngine()
    
    # Test package query
    result = engine.query("firefox", query_type="package")
    assert result is not None
    
    # Test option query
    result = engine.query("networking.firewall", query_type="option")
    assert result is not None


def test_knowledge_search():
    """Test knowledge search."""
    from luminous_nix.knowledge.engine import ModernNixOSKnowledgeEngine
    
    engine = ModernNixOSKnowledgeEngine()
    
    # Test search
    results = engine.search("editor", limit=5)
    assert isinstance(results, list)
    assert len(results) <= 5
