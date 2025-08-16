#!/usr/bin/env python3
"""
Test basic NLP intent recognition functionality.

Tests that the NLP system can correctly identify intents from natural language.
"""

import sys
import os
import unittest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from luminous_nix.core.intents import IntentRecognizer, IntentType


class TestNLPIntentRecognition(unittest.TestCase):
    """Test NLP intent recognition"""

    def setUp(self):
        """Set up intent recognizer"""
        self.recognizer = IntentRecognizer()

    def test_install_intent_recognition(self):
        """Test 1: Recognize install intent"""
        queries = [
            "install firefox",
            "I want to install vim",
            "please install python",
            "add firefox to my system",
            "get me the firefox browser"
        ]
        
        for query in queries:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.INSTALL_PACKAGE, 
                           f"Failed to recognize install intent in: {query}")

    def test_search_intent_recognition(self):
        """Test 2: Recognize search intent"""
        queries = [
            "search for python",
            "find markdown editor",
            "look for text editors",
            "what packages are available for python",
            "show me web browsers"
        ]
        
        for query in queries:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.SEARCH_PACKAGE,
                           f"Failed to recognize search intent in: {query}")

    def test_remove_intent_recognition(self):
        """Test 3: Recognize remove intent"""
        queries = [
            "remove vim",
            "uninstall firefox",
            "delete python package",
            "get rid of this package",
            "remove firefox from my system"
        ]
        
        for query in queries:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.REMOVE_PACKAGE,
                           f"Failed to recognize remove intent in: {query}")

    def test_update_intent_recognition(self):
        """Test 4: Recognize update intent"""
        queries = [
            "update my system",
            "upgrade all packages",
            "update firefox",
            "refresh my system",
            "rebuild my system"
        ]
        
        for query in queries:
            intent = self.recognizer.recognize(query)
            self.assertIn(intent.type, [IntentType.UPDATE_SYSTEM, IntentType.REBUILD],
                         f"Failed to recognize update intent in: {query}")

    def test_help_intent_recognition(self):
        """Test 5: Recognize help intent"""
        queries = [
            "help",
            "what can you do",
            "show me commands",
            "how do I use this",
            "list available commands"
        ]
        
        for query in queries:
            intent = self.recognizer.recognize(query)
            self.assertEqual(intent.type, IntentType.HELP,
                           f"Failed to recognize help intent in: {query}")

    def test_package_extraction(self):
        """Test 6: Extract package names from queries"""
        test_cases = [
            ("install firefox", "firefox"),
            ("remove vim editor", "vim"),
            ("search for python3", "python3"),
            ("update nodejs", "nodejs"),
            ("I want to install the firefox browser", "firefox")
        ]
        
        for query, expected_package in test_cases:
            intent = self.recognizer.recognize(query)
            self.assertIsNotNone(intent.entities)
            self.assertIn("package", intent.entities,
                         f"No package entity found in: {query}")
            self.assertEqual(intent.entities["package"], expected_package,
                           f"Wrong package extracted from: {query}")

    def test_ambiguous_queries(self):
        """Test 7: Handle ambiguous queries gracefully"""
        queries = [
            "firefox",  # Just a package name
            "python and rust",  # Multiple packages
            "something with markdown",  # Vague request
            "do the thing",  # Too vague
        ]
        
        for query in queries:
            intent = self.recognizer.recognize(query)
            # Should still return an intent, even if uncertain
            self.assertIsNotNone(intent)
            self.assertIsNotNone(intent.type)

    def test_confidence_scores(self):
        """Test 8: Check confidence scores"""
        high_confidence_queries = [
            "install firefox",
            "remove vim",
            "search python"
        ]
        
        low_confidence_queries = [
            "firefox",
            "something",
            "do stuff"
        ]
        
        for query in high_confidence_queries:
            intent = self.recognizer.recognize(query)
            self.assertGreater(intent.confidence, 0.7,
                             f"Low confidence for clear query: {query}")
        
        for query in low_confidence_queries:
            intent = self.recognizer.recognize(query)
            self.assertLess(intent.confidence, 0.5,
                          f"High confidence for vague query: {query}")


if __name__ == "__main__":
    unittest.main()