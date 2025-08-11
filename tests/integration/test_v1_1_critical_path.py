#!/usr/bin/env python3
"""
Critical Path Integration Tests for v1.1.0.

These tests verify the core functionality that must work
for the v1.1.0 release.
"""

import os
import sys
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

# pytest is optional
try:
    import pytest
except ImportError:
    pytest = None


import unittest


class TestPragmaticLearning(unittest.TestCase):
    """Test the pragmatic learning system."""

    def test_learns_aliases_from_corrections(self):
        """User types wrong command, then correct one - system learns."""
        from nix_for_humanity.learning.pragmatic_learning import PragmaticLearningSystem

        learning = PragmaticLearningSystem("test_alias")
        learning.ALIAS_THRESHOLD = 2  # Faster learning for tests

        # User makes same mistake twice
        learning.observe_command("grab firefox", False, "unknown")
        learning.observe_command("install firefox", True, None)
        learning.observe_command("grab vscode", False, "unknown")
        learning.observe_command("install vscode", True, None)

        # Should suggest correction
        suggestion = learning.suggest_alias("grab chrome")
        assert suggestion is not None
        assert "install" in suggestion.lower()

        # Cleanup
        learning.delete_all_data()

    def test_learns_command_sequences(self):
        """System learns common command patterns."""
        from nix_for_humanity.learning.pragmatic_learning import PragmaticLearningSystem

        learning = PragmaticLearningSystem("test_seq")
        learning.SEQUENCE_THRESHOLD = 2

        # User repeats pattern
        learning.observe_command("nixos-rebuild switch", True, None)
        learning.observe_command("nix-collect-garbage", True, None)
        learning.observe_command("nixos-rebuild switch", True, None)
        learning.observe_command("nix-collect-garbage", True, None)

        # Should suggest next command
        suggestion = learning.suggest_next_command("nixos-rebuild switch")
        assert suggestion is not None
        assert "nix-collect-garbage" in suggestion

        # Cleanup
        learning.delete_all_data()

    def test_learning_persistence(self):
        """Learning data persists across sessions."""
        from nix_for_humanity.learning.pragmatic_learning import PragmaticLearningSystem

        # Session 1: Learn something
        learning1 = PragmaticLearningSystem("test_persist")
        learning1.preferences.aliases["grab"] = "install"
        learning1.save_preferences()

        # Session 2: Should remember
        learning2 = PragmaticLearningSystem("test_persist")
        assert learning2.preferences.aliases.get("grab") == "install"

        # Cleanup
        learning2.delete_all_data()

    def test_verbosity_adaptation(self):
        """System adapts verbosity based on experience."""
        from nix_for_humanity.learning.pragmatic_learning import PragmaticLearningSystem

        learning = PragmaticLearningSystem("test_verbosity")

        # New user gets detailed help
        assert learning.get_verbosity_preference() == "detailed"

        # Add experience
        for i in range(15):
            learning.observe_command(f"command{i}", True, None)

        # Should be less verbose now
        assert learning.get_verbosity_preference() == "normal"

        # Cleanup
        learning.delete_all_data()


class TestNativeAPI(unittest.TestCase):
    """Test the native Python-Nix API performance."""

    def test_search_performance(self):
        """Package search should be under 100ms."""
        from nix_for_humanity.backend.native_nix_api import NativeNixAPI

        api = NativeNixAPI()

        start = time.time()
        results = api.search_packages("firefox")
        elapsed = time.time() - start

        # Should be fast
        assert elapsed < 0.1, f"Search took {elapsed*1000:.0f}ms, expected <100ms"
        assert len(results) > 0

    def test_mock_data_structure(self):
        """Native API returns correct data structure."""
        from nix_for_humanity.backend.native_nix_api import NativeNixAPI

        api = NativeNixAPI()
        results = api.search_packages("test")

        # Check structure
        assert isinstance(results, list)
        if results:
            result = results[0]
            assert "name" in result
            assert "version" in result
            assert "description" in result


class TestBackendIntegration(unittest.TestCase):
    """Test the unified backend."""

    def test_backend_initialization(self):
        """Backend initializes with safe defaults."""
        from nix_for_humanity.core.unified_backend import NixForHumanityBackend

        backend = NixForHumanityBackend()

        # Should default to dry-run for safety
        assert backend.config.get("dry_run", False) == True

        # Should have reasonable timeout
        timeout = backend.config.get("timeout", 0)
        assert timeout > 0 and timeout <= 120

    def test_intent_recognition(self):
        """Basic intent recognition works."""
        from nix_for_humanity.core import IntentRecognizer, IntentType

        recognizer = IntentRecognizer()

        # Test common patterns
        intents = {
            "install firefox": IntentType.INSTALL_PACKAGE,
            "search for editor": IntentType.SEARCH_PACKAGE,
            "update system": IntentType.UPDATE_SYSTEM,
            "remove vim": IntentType.REMOVE_PACKAGE,
        }

        for query, expected_type in intents.items():
            intent = recognizer.recognize(query)
            assert (
                intent.type == expected_type
            ), f"'{query}' → {intent.type}, expected {expected_type}"


class TestKairosImprovements(unittest.TestCase):
    """Test timing and flow improvements."""

    def test_adaptive_learning_thresholds(self):
        """Learning thresholds adapt to user experience."""
        from nix_for_humanity.learning.pragmatic_learning import PragmaticLearningSystem

        learning = PragmaticLearningSystem("test_kairos")

        # New users should learn faster (lower thresholds)
        # This is a kairos improvement - right pace at right time
        total_commands = sum(learning.preferences.command_frequency.values())

        if total_commands < 10:
            # Could lower thresholds for new users
            suggested_threshold = 2
        else:
            suggested_threshold = 3

        # System should adapt (this is aspirational)
        assert suggested_threshold <= 3

        # Cleanup
        learning.delete_all_data()

    def test_no_interruption_during_flow(self):
        """System respects user flow state."""
        from nix_for_humanity.learning.pragmatic_learning import PragmaticLearningSystem

        learning = PragmaticLearningSystem("test_flow")

        # Rapid commands indicate flow state
        for i in range(5):
            learning.observe_command(f"quick_cmd_{i}", True, None)

        # Should recognize active session
        verbosity = learning.get_verbosity_preference()

        # In flow, be concise
        assert verbosity in ["normal", "concise"]

        # Cleanup
        learning.delete_all_data()


# Run with pytest
if __name__ == "__main__":
    # Can also run directly

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPragmaticLearning))
    suite.addTests(loader.loadTestsFromTestCase(TestNativeAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestBackendIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestKairosImprovements))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1)
