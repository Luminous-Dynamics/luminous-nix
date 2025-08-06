"""
Shared test utilities for consciousness-first testing.

This module provides test implementations that replace mocks with
deterministic, real implementations that honor the principles of
consciousness-first development.
"""

from .test_implementations import (
    # Core test implementations
    TestProcess,
    TestExecutionBackend,
    TestProgressCallback,
    TestNLPEngine,
    TestDatabase,
    TestLearningEngine,
    TestBackendAPI,
    TestContextManager,
    TestKnowledgeBase,
    
    # Persona test data
    PERSONA_TEST_DATA,
    
    # Utility functions
    create_test_process,
    create_successful_process,
    create_failed_process,
    create_test_database,
    create_test_nlp_engine,
    
    # Test fixtures
    test_fixture,
    async_test_fixture,
    persona_test,
    performance_test,
)

__all__ = [
    # Core implementations
    'TestProcess',
    'TestExecutionBackend',
    'TestProgressCallback',
    'TestNLPEngine',
    'TestDatabase',
    'TestLearningEngine',
    'TestBackendAPI',
    'TestContextManager',
    'TestKnowledgeBase',
    
    # Test data
    'PERSONA_TEST_DATA',
    
    # Utilities
    'create_test_process',
    'create_successful_process',
    'create_failed_process',
    'create_test_database',
    'create_test_nlp_engine',
    
    # Fixtures
    'test_fixture',
    'async_test_fixture',
    'persona_test',
    'performance_test',
]