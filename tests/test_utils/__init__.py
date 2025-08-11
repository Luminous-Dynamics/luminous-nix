"""
Shared test utilities for consciousness-first testing.

This module provides test implementations that replace mocks with
deterministic, real implementations that honor the principles of
consciousness-first development.
"""

from .test_implementations import (  # Persona test data; Core test implementations; Utility functions; Test fixtures
    PERSONA_TEST_DATA,
    TestBackendAPI,
    TestContextManager,
    TestDatabase,
    TestExecutionBackend,
    TestKnowledgeBase,
    TestLearningEngine,
    TestNLPEngine,
    TestProcess,
    TestProgressCallback,
    async_test_fixture,
    create_failed_process,
    create_successful_process,
    create_test_database,
    create_test_nlp_engine,
    create_test_process,
    performance_test,
    persona_test,
    test_fixture,
)

__all__ = [
    # Core implementations
    "TestProcess",
    "TestExecutionBackend",
    "TestProgressCallback",
    "TestNLPEngine",
    "TestDatabase",
    "TestLearningEngine",
    "TestBackendAPI",
    "TestContextManager",
    "TestKnowledgeBase",
    # Test data
    "PERSONA_TEST_DATA",
    # Utilities
    "create_test_process",
    "create_successful_process",
    "create_failed_process",
    "create_test_database",
    "create_test_nlp_engine",
    # Fixtures
    "test_fixture",
    "async_test_fixture",
    "persona_test",
    "performance_test",
]
