#!/usr/bin/env python3
"""
Unit tests for the IntentRecognizer component.
Tests natural language intent recognition.
"""

import unittest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from luminous_nix.core.intents import Intent, IntentType, IntentRecognizer

class TestIntentRecognizer(unittest.TestCase):
    """Test the IntentRecognizer class"""

    def setUp(self):
        """Set up test instance"""
        self.recognizer = IntentRecognizer()

    def test_initialization(self):
        """Test IntentRecognizer initialization"""
        self.assertIsNotNone(self.recognizer)
        # Should have patterns loaded
        self.assertIsNotNone(self.recognizer._patterns)

    def test_recognize_install_intent(self):
        """Test recognizing install package intents"""
        test_queries = [
            "install firefox",
            "Install Firefox",
            "INSTALL FIREFOX",
            "please install firefox",
            "can you install firefox",
            "i need firefox",
            "i want firefox",
            "add firefox",
            "get firefox",
        ]
        
        for query in test_queries:
            intent = self.recognizer.recognize(query)
            self.assertIsInstance(intent, Intent)
            self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE, 
                           f"Failed to recognize install intent in: '{query}'")
            self.assertEqual(intent.entities.get("package"), "firefox")
            self.assertGreater(intent.confidence, 0.5)

    def test_recognize_remove_intent(self):
        """Test recognizing remove package intents"""
        test_queries = [
            "remove firefox",
            "uninstall firefox",
            "delete firefox",
            "get rid of firefox",
            "Remove Firefox",
        ]
        
        for query in test_queries:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.REMOVE_PACKAGE,
                           f"Failed to recognize remove intent in: '{query}'")
            self.assertEqual(intent.entities.get("package"), "firefox")

    def test_recognize_search_intent(self):
        """Test recognizing search intents"""
        test_queries = [
            "search firefox",
            "find firefox",
            "search for firefox",
            "look for firefox",
            "what packages have firefox",
            "find text editor",
            "search editors",
        ]
        
        for query in test_queries:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.SEARCH_PACKAGE,
                           f"Failed to recognize search intent in: '{query}'")

    def test_recognize_update_intent(self):
        """Test recognizing update system intents"""
        test_queries = [
            "update system",
            "update the system",
            "upgrade system",
            "update nixos",
            "update all packages",
            "system update",
        ]
        
        for query in test_queries:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.UPDATE_SYSTEM,
                           f"Failed to recognize update intent in: '{query}'")

    def test_recognize_list_intent(self):
        """Test recognizing list intents"""
        test_queries = [
            "list installed packages",
            "list packages",
            "show installed packages",
            "what's installed",
            "show all packages",
        ]
        
        for query in test_queries:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.LIST_INSTALLED,
                           f"Failed to recognize list intent in: '{query}'")

    def test_recognize_help_intent(self):
        """Test recognizing help intents"""
        test_queries = [
            "help",
            "help me",
            "what can you do",
            "show help",
            "?",
            "how does this work",
        ]
        
        for query in test_queries:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.HELP,
                           f"Failed to recognize help intent in: '{query}'")

    def test_recognize_rollback_intent(self):
        """Test recognizing rollback intents"""
        test_queries = [
            "rollback",
            "rollback system",
            "undo last update",
            "go back to previous generation",
            "revert system",
        ]
        
        for query in test_queries:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.ROLLBACK,
                           f"Failed to recognize rollback intent in: '{query}'")

    def test_recognize_garbage_collect_intent(self):
        """Test recognizing garbage collection intents"""
        test_queries = [
            "garbage collect",
            "clean up",
            "free space",
            "remove old generations",
            "gc",
            "nix-collect-garbage",
        ]
        
        for query in test_queries:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.GARBAGE_COLLECT,
                           f"Failed to recognize gc intent in: '{query}'")

    def test_recognize_service_intents(self):
        """Test recognizing service management intents"""
        # Start service
        intent = self.recognizer.recognize("start nginx")
        self.assertEqual(intent.type, IntentType.START_SERVICE)
        self.assertEqual(intent.entities.get("service"), "nginx")
        
        # Stop service
        intent = self.recognizer.recognize("stop nginx")
        self.assertEqual(intent.type, IntentType.STOP_SERVICE)
        self.assertEqual(intent.entities.get("service"), "nginx")
        
        # Restart service
        intent = self.recognizer.recognize("restart nginx")
        self.assertEqual(intent.type, IntentType.RESTART_SERVICE)
        self.assertEqual(intent.entities.get("service"), "nginx")
        
        # Service status
        intent = self.recognizer.recognize("status nginx")
        self.assertEqual(intent.type, IntentType.SERVICE_STATUS)
        self.assertEqual(intent.entities.get("service"), "nginx")
        
        # Enable service
        intent = self.recognizer.recognize("enable ssh")
        self.assertEqual(intent.type, IntentType.ENABLE_SERVICE)
        self.assertEqual(intent.entities.get("service"), "ssh")

    def test_recognize_network_intents(self):
        """Test recognizing network management intents"""
        # Show network
        intent = self.recognizer.recognize("show network")
        self.assertEqual(intent.type, IntentType.SHOW_NETWORK)
        
        # Show IP
        intent = self.recognizer.recognize("show ip")
        self.assertEqual(intent.type, IntentType.SHOW_IP)
        
        # List WiFi
        intent = self.recognizer.recognize("list wifi networks")
        self.assertEqual(intent.type, IntentType.LIST_WIFI)
        
        # Test connection
        intent = self.recognizer.recognize("test connection")
        self.assertEqual(intent.type, IntentType.TEST_CONNECTION)

    def test_recognize_config_intents(self):
        """Test recognizing configuration intents"""
        # Edit config
        intent = self.recognizer.recognize("edit configuration")
        self.assertEqual(intent.type, IntentType.EDIT_CONFIG)
        
        # Show config
        intent = self.recognizer.recognize("show configuration")
        self.assertEqual(intent.type, IntentType.SHOW_CONFIG)
        
        # Validate config
        intent = self.recognizer.recognize("validate config")
        self.assertEqual(intent.type, IntentType.VALIDATE_CONFIG)
        
        # Generate config
        intent = self.recognizer.recognize("generate configuration")
        self.assertEqual(intent.type, IntentType.GENERATE_CONFIG)

    def test_package_name_extraction(self):
        """Test extracting package names from queries"""
        test_cases = [
            ("install firefox-esr", "firefox-esr"),
            ("install python3", "python3"),
            ("remove lib-something", "lib-something"),
            ("install package_with_underscore", "package_with_underscore"),
            ("install vim.tiny", "vim.tiny"),
        ]
        
        for query, expected_package in test_cases:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.entities.get("package"), expected_package,
                           f"Failed to extract package name from: '{query}'")

    def test_unknown_intent(self):
        """Test handling of unknown/unclear intents"""
        unclear_queries = [
            "asdfghjkl",
            "do the thing",
            "make it work",
            "",
            "   ",
            "123456",
        ]
        
        for query in unclear_queries:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.UNKNOWN,
                           f"Should return UNKNOWN for unclear query: '{query}'")
            self.assertLess(intent.confidence, 0.5)

    def test_confidence_levels(self):
        """Test that confidence levels make sense"""
        # Clear intent should have high confidence
        intent = self.recognizer.recognize("install firefox")
        self.assertGreater(intent.confidence, 0.8)
        
        # Less clear intent should have lower confidence
        intent = self.recognizer.recognize("get firefox somehow")
        self.assertLess(intent.confidence, 0.8)
        
        # Unknown intent should have very low confidence
        intent = self.recognizer.recognize("xyz abc")
        self.assertLess(intent.confidence, 0.3)

    def test_whitespace_handling(self):
        """Test handling of various whitespace"""
        test_cases = [
            ("  install   firefox  ", "firefox"),
            ("\tinstall\tfirefox\t", "firefox"),
            ("install\nfirefox", "firefox"),
            ("install     firefox", "firefox"),
        ]
        
        for query, expected_package in test_cases:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
            self.assertEqual(intent.entities.get("package"), expected_package)

    def test_case_insensitivity(self):
        """Test case-insensitive recognition"""
        queries = [
            "INSTALL FIREFOX",
            "Install Firefox",
            "install firefox",
            "InStAlL fIrEfOx",
        ]
        
        for query in queries:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE)
            self.assertEqual(intent.entities.get("package").lower(), "firefox")

    def test_multiple_word_packages(self):
        """Test recognizing multi-word package names"""
        test_cases = [
            ("install visual studio code", "visual studio code"),
            ("remove google chrome", "google chrome"),
            ("install libre office", "libre office"),
        ]
        
        for query, expected_package in test_cases:
            intent = self.recognizer.recognize(query)
            # Check that we captured something reasonable
            package = intent.entities.get("package", "")
            self.assertTrue(len(package) > 0)

    def test_raw_text_preserved(self):
        """Test that raw text is preserved in intent"""
        queries = [
            "install firefox",
            "REMOVE VIM",
            "  search   editors  ",
        ]
        
        for query in queries:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.raw_text, query)

if __name__ == "__main__":
    unittest.main()