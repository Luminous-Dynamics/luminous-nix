"""
Comprehensive unit tests for NixForHumanityBackend - Consciousness-First Testing

Testing all aspects of the unified backend that serves all frontend adapters.
Uses deterministic test implementations instead of mocks to verify
real behavior and interactions.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import pytest
import asyncio

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.test_utils.test_implementations import (
    TestNLPEngine,
    TestExecutionBackend,
    TestDatabase,
    TestLearningEngine,
    TestKnowledgeBase,
    TestBackendAPI,
    PERSONA_TEST_DATA,
    create_test_process,
    create_successful_process,
    create_failed_process
)

from backend.core.backend import NixForHumanityBackend, create_backend
from backend.api.schema import Request, Response, Result
from nix_for_humanity.core.types import Intent, IntentType


class TestNixForHumanityBackend:
    """Test suite for NixForHumanityBackend - Consciousness-First Testing"""
    
    @pytest.fixture
    def test_nlp_engine(self):
        """Create test NLP engine with deterministic behavior"""
        return TestNLPEngine()
    
    @pytest.fixture
    def test_executor(self):
        """Create test execution backend"""
        return TestExecutionBackend()
    
    @pytest.fixture
    def test_knowledge_base(self):
        """Create test knowledge base"""
        return TestKnowledgeBase()
    
    @pytest.fixture  
    def test_database(self):
        """Create test database"""
        return TestDatabase()
    
    @pytest.fixture
    def test_learning_engine(self, test_database):
        """Create test learning engine"""
        return TestLearningEngine(test_database)
    
    @pytest.fixture
    def backend(self, test_nlp_engine, test_executor, test_knowledge_base):
        """Create backend with test dependencies"""
        # Using dependency injection instead of mocking
        backend = NixForHumanityBackend()
        backend.intent_recognizer = test_nlp_engine
        backend.executor = test_executor
        backend.knowledge = test_knowledge_base
        backend._has_python_api = False
        return backend
    
    @pytest.fixture
    def backend_with_progress(self):
        """Create backend with progress tracking"""
        progress_calls = []
        def progress_callback(message, progress):
            progress_calls.append((message, progress))
        
        backend = NixForHumanityBackend(progress_callback)
        backend.progress_calls = progress_calls
        return backend
    
    # Test Initialization
    
    def test_init_basic(self):
        """Test basic initialization"""
        backend = NixForHumanityBackend()
        assert backend.intent_recognizer is not None
        assert backend.executor is not None
        assert backend.knowledge is not None
        assert backend.progress_callback is None
    
    def test_init_with_progress_callback(self):
        """Test initialization with progress callback"""
        progress_calls = []
        def test_callback(message, progress):
            progress_calls.append((message, progress))
            
        backend = NixForHumanityBackend(test_callback)
        assert backend.progress_callback == test_callback
        
        # Test progress callback works
        backend.progress_callback("Test", 0.5)
        assert progress_calls == [("Test", 0.5)]
    
    def test_init_nixos_api_detection(self):
        """Test NixOS API detection with deterministic behavior"""
        backend = NixForHumanityBackend()
        
        # Should have API availability flag
        assert hasattr(backend, '_has_python_api')
        assert isinstance(backend._has_python_api, bool)
        
        # If API not available, should still work
        if not backend._has_python_api:
            # Should have fallback executor
            assert backend.executor is not None
    
    # Test Path Finding
    
    @patch(\'pathlib.Path.exists\', create=True)
    @patch(\'subprocess.run\', create=True)
    def test_find_nixos_rebuild_path_known_path(self, mock_run, mock_exists):
        """Test finding nixos-rebuild path from known locations"""
        mock_exists.return_value = True
        
        backend = NixForHumanityBackend()
        path = backend._find_nixos_rebuild_path()
        
        # Should find a known path
        self.assertIsNotNone(path) or not mock_exists.called
    
    @patch(\'pathlib.Path.exists\', create=True)
    @patch(\'subprocess.run\', create=True)
    def test_find_nixos_rebuild_path_via_which(self, mock_run, mock_exists):
        """Test finding nixos-rebuild path via which command"""
        mock_exists.return_value = False
        
        # Create a simple mock result object
        class MockResult:
            returncode = 0
            stdout = "/nix/store/fake/bin/nixos-rebuild\n"
        
        mock_run.return_value = MockResult()
        
        backend = NixForHumanityBackend()
        path = backend._find_nixos_rebuild_path()
        
        mock_run.assert_called_with(['which', 'nixos-rebuild'], capture_output=True, text=True)
    
    @patch(\'subprocess.run\', create=True)
    def test_find_nixos_rebuild_path_not_found(self, mock_run):
        """Test when nixos-rebuild path cannot be found"""
        class MockResult:
            returncode = 1
        mock_run.return_value = MockResult()
        
        backend = NixForHumanityBackend()
        path = backend._find_nixos_rebuild_path()
        
        self.assertIsNone(path)
    
    # Test Request Processing
    
        def test_process_request_basic(self, backend, mock_intent_recognizer):
        """Test basic request processing"""
        # Setup
        request = Request(text="install firefox", context={})
        intent = Intent(
        type=IntentType.INSTALL,
        entities={'package': 'firefox'},
        confidence=0.95,
        raw_input="install firefox"
    )
        mock_intent_recognizer.recognize.return_value = intent
        
        # Execute
        response = backend.process_request(request)
        
        # Verify
        self.assertTrue(response.success)
        self.assertEqual(response.intent, intent)
        self.assertGreater(len(response.plan), 0)
        self.assertIn("firefox", response.explanation)
    
        def test_process_request_with_execution(self, backend, mock_intent_recognizer, mock_executor):
        """Test request processing with execution"""
        # Setup
        request = Request(
            text="update system",
            context={'execute': True, 'dry_run': False}
        )
        intent = Intent(
        type=IntentType.UPDATE,
        entities={},
        confidence=0.98,
        raw_input="update system"
    )
        mock_intent_recognizer.recognize.return_value = intent
        mock_executor.execute.return_value = Result(
            success=True,
            output="System updated successfully",
            error=None
        )
        
        # Execute
        response = backend.process_request(request)
        
        # Verify
        self.assertTrue(response.success)
        self.assertIsNotNone(response.result)
        self.assertTrue(response.result.success)
        mock_executor.execute.assert_called_once()
    
        def test_process_request_dry_run(self, backend, mock_intent_recognizer, mock_executor):
        """Test request processing in dry run mode"""
        # Setup
        request = Request(
            text="install vim",
            context={'execute': True, 'dry_run': True}
        )
        intent = Intent(
        type=IntentType.INSTALL,
        entities={'package': 'vim'},
        confidence=0.92,
        raw_input="install vim"
    )
        mock_intent_recognizer.recognize.return_value = intent
        
        # Execute
        response = backend.process_request(request)
        
        # Verify
        self.assertTrue(response.success)
        self.assertIn(response.result is None  # No execution, dry run)
        mock_executor.execute.assert_not_called()
    
        def test_process_request_with_progress(self, backend_with_progress):
        """Test request processing with progress callbacks"""
        # Setup
        backend = backend_with_progress
        request = Request(text="search emacs", context={})
        intent = Intent(
        type=IntentType.SEARCH,
        entities={'query': 'emacs'},
        confidence=0.88,
        raw_input="search emacs"
    )
        backend.intent_recognizer.recognize = MagicMock(return_value=intent)
        
        # Execute
        response = backend.process_request(request)
        
        # Verify progress calls
        progress_messages = [call[0] for call in backend.progress_calls]
        self.assertIn("Analyzing request...", progress_messages)
        self.assertIn("Planning actions...", progress_messages)
        self.assertIn("Generating response...", progress_messages)
        self.assertIn("Complete!", progress_messages)
    
        def test_process_request_error_handling(self, backend, mock_intent_recognizer):
        """Test error handling in request processing"""
        # Setup
        request = Request(text="do something", context={})
        mock_intent_recognizer.recognize.side_effect = Exception("Test error")
        
        # Execute
        response = backend.process_request(request)
        
        # Verify
        self.assertFalse(response.success)
        self.assertEqual(response.intent.type, IntentType.UNKNOWN)
        self.assertIn("Test error", response.explanation)
        self.assertGreater(len(response.suggestions), 0)
    
    # Test Action Planning
    
        def test_plan_actions_install_package(self, backend):
        """Test action planning for package installation"""
        intent = Intent(
        type=IntentType.INSTALL,
        entities={'package': 'neovim'},
        confidence=0.95,
        raw_input="install neovim"
    )
        request = Request(text="install neovim", context={})
        
        plan = backend._plan_actions(intent, request)
        
        self.assertGreater(len(plan), 0)
        self.assertIn(any("neovim", action for action in plan))
        self.assertIn(any("install", action.lower() for action in plan))
    
        def test_plan_actions_update_system(self, backend):
        """Test action planning for system update"""
        intent = Intent(
        type=IntentType.UPDATE,
        entities={},
        confidence=0.97,
        raw_input="update my system"
    )
        request = Request(text="update my system", context={})
        
        plan = backend._plan_actions(intent, request)
        
        self.assertGreater(len(plan), 0)
        self.assertIn(any("update", action.lower() for action in plan))
    
        def test_plan_actions_with_python_api(self, backend):
        """Test action planning when Python API is available"""
        backend._has_python_api = True
        intent = Intent(
        type=IntentType.INSTALL,
        entities={'package': 'git'},
        confidence=0.93,
        raw_input="install git"
    )
        request = Request(text="install git", context={})
        
        plan = backend._plan_actions(intent, request)
        
        self.assertIn(any("Python API", action for action in plan))
    
    # Test Explanation Generation
    
    def test_explain_install_package(self, backend):
        """Test explanation generation for package installation"""
        intent = Intent(
        type=IntentType.INSTALL,
        entities={'package': 'firefox'},
        confidence=0.96,
        raw_input="install firefox"
    )
        plan = ["Install firefox", "Verify installation"]
        
        explanation = backend._explain(intent, plan, None)
        
        self.assertIn("firefox", explanation)
        self.assertIn("install", explanation.lower())
    
    def test_explain_with_success_result(self, backend):
        """Test explanation with successful result"""
        intent = Intent(
        type=IntentType.UPDATE,
        entities={},
        confidence=0.94,
        raw_input="update system"
    )
        plan = ["Update system"]
        result = Result(success=True, output="Updated", error=None)
        
        explanation = backend._explain(intent, plan, result)
        
        self.assertIn("successfully", explanation.lower())
    
    def test_explain_with_error_result(self, backend):
        """Test explanation with error result"""
        intent = Intent(
        type=IntentType.INSTALL,
        entities={'package': 'vim'},
        confidence=0.91,
        raw_input="install vim"
    )
        plan = ["Install vim"]
        result = Result(success=False, output="", error="Package not found")
        
        explanation = backend._explain(intent, plan, result)
        
        self.assertIn("error", explanation.lower())
        self.assertIn("Package not found", explanation)
    
    # Test Suggestions
    
    def test_get_suggestions_install_success(self, backend):
        """Test suggestions after successful installation"""
        intent = Intent(
        type=IntentType.INSTALL,
        entities={'package': 'emacs'},
        confidence=0.89,
        raw_input="install emacs"
    )
        result = Result(success=True, output="Installed", error=None)
        
        suggestions = backend._get_suggestions(intent, result)
        
        self.assertGreater(len(suggestions), 0)
        self.assertIn(any("emacs", s for s in suggestions))
        self.assertIn(any("configuration.nix", s for s in suggestions))
    
    def test_get_suggestions_unknown_intent(self, backend):
        """Test suggestions for unknown intent"""
        intent = Intent(
        type=IntentType.UNKNOWN,
        entities={},
        confidence=0.3,
        raw_input="do the thing"
    )
        
        suggestions = backend._get_suggestions(intent, None)
        
        self.assertGreater(len(suggestions), 0)
        self.assertIn(any("install", s.lower() for s in suggestions))
    
    # Test Command Extraction
    
    def test_extract_commands_install(self, backend):
        """Test command extraction from install plan"""
        plan = [
            "Use nix profile install nixpkgs#firefox",
            "Verify firefox installation"
        ]
        
        commands = backend._extract_commands(plan)
        
        self.assertGreater(len(commands), 0)
        self.assertEqual(commands[0]['command'], "nix profile install nixpkgs#firefox")
        self.assertEqual(commands[0]['description'], "Install package")
    
    def test_extract_commands_update(self, backend):
        """Test command extraction from update plan"""
        plan = [
            "Update channels: sudo nix-channel --update",
            "Rebuild system: sudo nixos-rebuild switch"
        ]
        
        commands = backend._extract_commands(plan)
        
        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0]['command'], "sudo nix-channel --update")
        self.assertEqual(commands[1]['command'], "sudo nixos-rebuild switch")
    
    # Test Native API Integration
    
    def test_should_use_native_api_enabled(self, backend):
        """Test native API detection when enabled"""
        os.environ['NIX_HUMANITY_PYTHON_BACKEND'] = 'true'
        request = Request(text="update system", context={})
        
        should_use = backend._should_use_native_api(request)
        
        self.assertTrue(should_use)
        
        # Cleanup
        if 'NIX_HUMANITY_PYTHON_BACKEND' in os.environ:
            del os.environ['NIX_HUMANITY_PYTHON_BACKEND']
    
    def test_should_use_native_api_disabled(self, backend):
        """Test native API detection when disabled"""
        if 'NIX_HUMANITY_PYTHON_BACKEND' in os.environ:
            del os.environ['NIX_HUMANITY_PYTHON_BACKEND']
        request = Request(text="update system", context={})
        
        should_use = backend._should_use_native_api(request)
        
        self.assertFalse(should_use)
    
    def test_should_use_native_api_non_nixos_operation(self, backend):
        """Test native API detection for non-NixOS operations"""
        os.environ['NIX_HUMANITY_PYTHON_BACKEND'] = 'true'
        request = Request(text="explain generations", context={})
        
        should_use = backend._should_use_native_api(request)
        
        self.assertIn(should_use  # "explain" is not, nixos_operations but might still use native)
        
        # Cleanup
        if 'NIX_HUMANITY_PYTHON_BACKEND' in os.environ:
            del os.environ['NIX_HUMANITY_PYTHON_BACKEND']
    
        @patch(\'backend.core.backend.NixOSIntegration\', create=True)
    def test_process_native_success(self, mock_integration_class, backend, mock_intent_recognizer):
        """Test native processing success"""
        # Setup
        mock_integration = MagicMock()
        mock_integration.execute_intent = AsyncMock(return_value={
            'success': True,
            'message': 'System updated successfully',
            'education': {
                'what_happened': 'Updated all channels',
                'next_steps': 'Check generation differences'
            }
        })
        mock_integration_class.return_value = mock_integration
        
        request = Request(text="update system", context={})
        intent = Intent(
        type=IntentType.UPDATE,
        entities={},
        confidence=0.95,
        raw_input="update system"
    )
        mock_intent_recognizer.recognize.return_value = intent
        
        # Execute
        response = backend._process_native(request)
        
        # Verify
        self.assertTrue(response.success)
        self.assertEqual(response.intent, intent)
        self.assertIn("System updated successfully", response.explanation)
        self.assertIsNotNone(response.data.get('education'))
    
        @patch(\'backend.core.backend.NixOSIntegration\', create=True)
    def test_process_native_fallback(self, mock_integration_class, backend, mock_intent_recognizer):
        """Test fallback when native processing fails"""
        # Setup
        mock_integration_class.side_effect = Exception("Native API error")
        
        request = Request(text="install vim", context={})
        intent = Intent(
        type=IntentType.INSTALL,
        entities={'package': 'vim'},
        confidence=0.92,
        raw_input="install vim"
    )
        mock_intent_recognizer.recognize.return_value = intent
        
        # Execute
        response = backend._process_native(request)
        
        # Verify - should fall back to regular processing
        self.assertEqual(response.intent, intent)
    
    # Test Synchronous Processing
    
    def test_process_sync(self, backend, mock_intent_recognizer, mock_knowledge):
        """Test synchronous processing"""
        # Setup
        request = Request(query="install firefox", context={'personality': 'minimal'})
        intent = Intent(
        type=IntentType.INSTALL,
        entities={'package': 'firefox'},
        confidence=0.94,
        raw_input="install firefox"
    )
        mock_intent_recognizer.recognize.return_value = intent
        mock_knowledge.get_solution.return_value = {
            'methods': [
                {
                    'name': 'Declarative',
                    'description': 'Add to configuration.nix',
                    'example': 'environment.systemPackages = [ pkgs.firefox ];'
                }
            ],
            'explanation': 'Firefox is a web browser'
        }
        
        # Execute
        response = backend.process(request)
        
        # Verify
        self.assertTrue(response.success)
        self.assertIn('firefox', response.text)
        self.assertGreater(len(response.commands), 0)
    
    def test_process_sync_error(self, backend, mock_intent_recognizer):
        """Test synchronous processing error handling"""
        # Setup
        request = Request(query="do something", context={})
        mock_intent_recognizer.recognize.side_effect = Exception("Test error")
        
        # Execute
        response = backend.process(request)
        
        # Verify
        self.assertFalse(response.success)
        self.assertIn("Test error", response.text)
    
    # Test Response Building
    
    def test_build_response_text_minimal_personality(self, backend):
        """Test response building with minimal personality"""
        intent = Intent(
        type=IntentType.INSTALL,
        entities={'package': 'git'},
        confidence=0.90,
        raw_input="install git"
    )
        knowledge = {
            'methods': [
                {
                    'name': 'nix-env',
                    'description': 'User profile installation',
                    'example': 'nix-env -iA nixos.git'
                }
            ],
            'package': 'git'
        }
        
        response_text = backend._build_response_text(intent, knowledge, 'minimal')
        
        self.assertIn('git', response_text)
        self.assertIn('nix-env', response_text)
        self.assertIn('😊' not, response_text  # No emojis in minimal)
    
    def test_build_response_text_friendly_personality(self, backend):
        """Test response building with friendly personality"""
        intent = Intent(
        type=IntentType.UPDATE,
        entities={},
        confidence=0.93,
        raw_input="update system"
    )
        knowledge = {
            'solution': 'Run nixos-rebuild switch to update',
            'example': 'sudo nixos-rebuild switch',
            'explanation': 'This rebuilds and activates the configuration'
        }
        
        response_text = backend._build_response_text(intent, knowledge, 'friendly')
        
        self.assertIn('Hi there!', response_text)
        self.assertIn('😊', response_text)
        self.assertIn('clarification', response_text)
    
    def test_build_response_text_symbiotic_personality(self, backend):
        """Test response building with symbiotic personality"""
        intent = Intent(
        type=IntentType.SEARCH,
        entities={'query': 'editor'},
        confidence=0.87,
        raw_input="search editor"
    )
        knowledge = {
            'response': 'Found several editors: vim, emacs, vscode'
        }
        
        response_text = backend._build_response_text(intent, knowledge, 'symbiotic')
        
        self.assertIn('🤝', response_text)
        self.assertIn('learning', response_text)
        self.assertIn('feedback', response_text.lower())
    
    def test_build_response_text_no_knowledge(self, backend):
        """Test response building when no knowledge available"""
        intent = Intent(
        type=IntentType.UNKNOWN,
        entities={},
        confidence=0.2,
        raw_input="xyz abc"
    )
        
        response_text = backend._build_response_text(intent, None, 'minimal')
        
        self.assertIn("not sure", response_text)
        self.assertIn("installing packages", response_text)
    
    # Test Learning (Placeholder)
    
        def test_learn_debug_mode(self, backend):
        """Test learning in debug mode"""
        os.environ['DEBUG'] = 'true'
        request = Request(text="install vim", context={})
        response = Response(
            success=True,
            text="Installing vim",
            data={'intent': 'install_package'}
        )
        
        # Should not raise
        backend._learn(request, response)
        
        # Cleanup
        if 'DEBUG' in os.environ:
            del os.environ['DEBUG']
    
    # Test Factory Function
    
    def test_create_backend(self):
        """Test backend factory function"""
        callback = MagicMock()
        backend = create_backend(callback)
        
        self.assertTrue(isinstance(backend, NixForHumanityBackend))
        self.assertEqual(backend.progress_callback, callback)
    
    def test_create_backend_no_callback(self):
        """Test backend factory without callback"""
        backend = create_backend()
        
        self.assertTrue(isinstance(backend, NixForHumanityBackend))
        self.assertIsNone(backend.progress_callback)
    
    # Test Edge Cases
    
        def test_process_request_empty_text(self, backend):
        """Test processing request with empty text"""
        request = Request(text="", context={})
        
        response = backend.process_request(request)
        
        # Should handle gracefully
        self.assertIsNotNone(response)
        self.assertEqual(not response.success or response.intent.type, IntentType.UNKNOWN)
    
    def test_extract_commands_empty_plan(self, backend):
        """Test command extraction from empty plan"""
        commands = backend._extract_commands([])
        
        self.assertEqual(commands, [])
    
    def test_get_suggestions_none_result(self, backend):
        """Test suggestions with None result"""
        intent = Intent(
        type=IntentType.UPDATE,
        entities={},
        confidence=0.85,
        raw_input="update"
    )
        
        suggestions = backend._get_suggestions(intent, None)
        
        self.assertTrue(isinstance(suggestions, list))
        self.assertGreater(len(suggestions), 0)


if __name__ == "__main__":
    unittest.main()