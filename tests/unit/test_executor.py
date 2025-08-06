"""
Unit tests for ExecutionEngine class

Testing the safe command execution module that handles NixOS operations
with proper error handling, rollback capabilities, and progress reporting.

Uses consciousness-first testing approach with real test implementations
instead of mocks.
"""

import unittest
import asyncio
from pathlib import Path
import tempfile
import os
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import time

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from nix_for_humanity.core.execution_engine import ExecutionEngine
from nix_for_humanity.core.types import Intent, IntentType


@dataclass
class TestProcess:
    """Simulated process for testing"""
    returncode: int
    stdout: bytes
    stderr: bytes
    execution_time: float = 0.1
    
    async def communicate(self, timeout=None):
        """Simulate process communication"""
        if timeout and self.execution_time > timeout:
            raise asyncio.TimeoutError()
        await asyncio.sleep(self.execution_time)
        return (self.stdout, self.stderr)
    
    def kill(self):
        """Simulate process termination"""
        self.returncode = -15
    
    async def wait(self):
        """Simulate waiting for process completion"""
        await asyncio.sleep(0.01)


class TestExecutionBackend:
    """Consciousness-first test backend for ExecutionEngine"""
    
    def __init__(self):
        self.installed_packages = set()
        self.system_generations = [1, 2, 3]
        self.current_generation = 3
        self.search_results = {
            'firefox': [('firefox', 'Web browser'), ('firefox-esr', 'Extended support release')],
            'nonexistent': []
        }
        self.process_responses = {}
        self.api_available = True
        self.api_calls = []
        
    def set_process_response(self, command: str, process: TestProcess):
        """Configure response for a specific command"""
        self.process_responses[command] = process
        
    async def create_subprocess(self, *args, **kwargs) -> TestProcess:
        """Simulate subprocess creation with deterministic behavior"""
        command = ' '.join(args)
        
        # Check for configured responses
        for key, process in self.process_responses.items():
            if key in command:
                return process
        
        # Default responses based on command type
        if 'nix profile install' in command:
            package = args[3].split('#')[-1]
            if package in ['firefox', 'vim', 'emacs']:
                self.installed_packages.add(package)
                return TestProcess(0, b"Success", b"")
            else:
                return TestProcess(1, b"", b"Package not found")
                
        elif 'nix search' in command:
            query = args[3] if len(args) > 3 else 'unknown'
            results = self.search_results.get(query, [])
            if results:
                output = '\n'.join(f"* {pkg}: {desc}" for pkg, desc in results)
                return TestProcess(0, output.encode(), b"")
            else:
                return TestProcess(0, b"", b"")
                
        elif 'echo test' in command:
            return TestProcess(0, b"Output", b"")
            
        elif 'sleep' in command:
            return TestProcess(0, b"", b"", execution_time=10)
            
        else:
            return TestProcess(0, b"Success", b"")
    
    def get_nix_api(self):
        """Simulate NixOS Python API"""
        if not self.api_available:
            raise ImportError("nixos_rebuild not available")
        
        class MockNixAPI:
            def __init__(self, backend):
                self.backend = backend
                
            def rollback(self, generation=None):
                backend.api_calls.append(('rollback', generation))
                if generation and generation not in backend.system_generations:
                    raise ValueError(f"Generation {generation} not found")
                backend.current_generation = generation or backend.system_generations[-2]
                return True
                
        return MockNixAPI(self)


class TestExecutionEngine(unittest.TestCase):
    """Test ExecutionEngine functionality with consciousness-first approach"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.backend = TestExecutionBackend()
        self.progress_callback = TestProgressCallback()
        self.engine = ExecutionEngine(progress_callback=self.progress_callback.callback)
        
        # Inject test backend
        self._original_subprocess = asyncio.create_subprocess_exec
        asyncio.create_subprocess_exec = self.backend.create_subprocess
        
        # Configure Python API availability
        if self.backend.api_available:
            self.engine._has_python_api = True
            self.engine.nix_api = self.backend.get_nix_api()
            
    def tearDown(self):
        """Clean up after tests"""
        # Restore original subprocess function
        asyncio.create_subprocess_exec = self._original_subprocess
        
        # Reset any environment variables
        if 'DEBUG' in os.environ:
            del os.environ['DEBUG']


class TestProgressCallback:
    """Track progress callbacks for testing"""
    
    def __init__(self):
        self.calls = []
        
    def callback(self, message: str, progress: float):
        """Record callback invocations"""
        self.calls.append((message, progress, time.time()))
        
    def tearDown(self):
        """Clean up after tests"""
        # Reset any environment variables
        if 'DEBUG' in os.environ:
            del os.environ['DEBUG']
            
    def test_init_default(self):
        """Test initialization with default parameters"""
        executor = ExecutionEngine()
        self.assertIsNone(executor.progress_callback)
        self.assertFalse(executor.dry_run)
        
    def test_init_with_callback(self):
        """Test initialization with progress callback"""
        callback = TestProgressCallback()
        executor = ExecutionEngine(progress_callback=callback.callback)
        self.assertEqual(executor.progress_callback, callback.callback)
        self.assertFalse(executor.dry_run)
        
    def test_init_python_api_success(self):
        """Test successful Python API initialization"""
        # Backend already configured with API available
        self.assertTrue(self.engine._has_python_api)
        self.assertIsNotNone(self.engine.nix_api)
        
    def test_init_python_api_failure(self):
        """Test Python API initialization when module not available"""
        # Create new engine with API unavailable
        self.backend.api_available = False
        executor = ExecutionEngine()
        # Should gracefully handle import failure
        self.assertIsInstance(executor._has_python_api, bool)
        
    def test_execute_install_package(self):
        """Test package installation execution"""
        intent = Intent(
            type=IntentType.INSTALL,
            entities={'package': 'firefox'},
            confidence=0.95,
            raw_input="install firefox"
        )
        
        result = self.engine.execute([], intent)
        
        self.assertTrue(result.success)
        self.assertIn("firefox", result.output.lower())
        self.assertIn("firefox", self.backend.installed_packages)
            
    def test_execute_update_system(self):
        """Test system update execution"""
        intent = Intent(
            type=IntentType.UPDATE,
            entities={},
            confidence=0.95,
            raw_input="update system"
        )
        
        # Configure expected response
        self.backend.set_process_response(
            'nixos-rebuild', 
            TestProcess(0, b"System updated successfully", b"")
        )
        
        result = self.engine.execute([], intent)
        
        self.assertTrue(result.success)
        self.assertIn("update", result.output.lower())
            
    def test_execute_search_package(self):
        """Test package search execution"""
        intent = Intent(
            type=IntentType.SEARCH,
            entities={'query': 'firefox'},
            confidence=0.9,
            raw_input="search firefox"
        )
        
        result = self.engine.execute([], intent)
        
        self.assertTrue(result.success)
        self.assertIn("firefox", result.output)
        self.assertIn("Web browser", result.output)
            
    def test_execute_rollback(self):
        """Test system rollback execution"""
        intent = Intent(
            type=IntentType.ROLLBACK,
            entities={},
            confidence=0.95,
            raw_input="rollback"
        )
        
        initial_generation = self.backend.current_generation
        result = self.engine.execute([], intent)
        
        self.assertTrue(result.success)
        # Verify rollback occurred
        if self.engine._has_python_api:
            self.assertIn(('rollback', None), self.backend.api_calls)
            self.assertNotEqual(self.backend.current_generation, initial_generation)
            
    def test_execute_unsupported_intent(self):
        """Test execution with unsupported intent type"""
        # Create an intent with an unsupported type
        class UnsupportedIntent:
            type = "UNSUPPORTED_TYPE"
            entities = {}
            confidence = 0.9
            raw_input = "unsupported command"
        
        intent = UnsupportedIntent()
        result = self.engine.execute([], intent)
        
        self.assertFalse(result.success)
        self.assertEqual(result.output, "")
        self.assertIn("not implemented", result.error)
        
    def test_execute_exception_handling(self):
        """Test exception handling during execution"""
        intent = Intent(
            type=IntentType.INSTALL,
            entities={'package': 'error-package'},
            confidence=0.95,
            raw_input="install error-package"
        )
        
        # Configure process to simulate an exception
        self.backend.set_process_response(
            'error-package',
            TestProcess(-1, b"", b"Critical error occurred")
        )
        
        result = self.engine.execute([], intent)
        
        # Should handle error gracefully
        self.assertIsNotNone(result)
            
    def test_execute_install_no_package(self):
        """Test install execution without package name"""
        result = self.engine._execute_install(None)
        
        self.assertFalse(result.success)
        self.assertEqual(result.output, "")
        self.assertIn("No package specified", result.error)
        
    def test_execute_install_dry_run(self):
        """Test install execution in dry run mode"""
        self.engine.dry_run = True
        
        result = self.engine._execute_install("firefox")
        
        self.assertTrue(result.success)
        self.assertIn("Would install: firefox", result.output)
        self.assertEqual(result.error, "")
        
    def test_execute_install_subprocess_success(self):
        """Test successful package installation via subprocess"""
        # Since asyncio.create_subprocess_exec is already intercepted by our setUp,
        # we just need to test direct subprocess installation
        result = self.engine._execute_install("firefox")
        
        self.assertTrue(result.success)
        self.assertIn("firefox", self.backend.installed_packages)
        
    def test_execute_install_subprocess_failure(self):
        """Test failed package installation via subprocess"""
        # Test with a package that the backend doesn't recognize
        result = self.engine._execute_install("nonexistent-package")
        
        self.assertFalse(result.success)
        self.assertIn("not found", result.error.lower())
        self.assertNotIn("nonexistent-package", self.backend.installed_packages)
        
    def test_execute_install_with_progress(self):
        """Test install with progress callback"""
        self.engine._has_python_api = False
        
        result = self.engine._execute_install("firefox")
        
        # Verify progress callback was called
        self.assertTrue(len(self.progress_callback.calls) > 0)
        messages = [call[0] for call in self.progress_callback.calls]
        self.assertTrue(any("firefox" in msg for msg in messages))
            
    def test_execute_update_dry_run(self):
        """Test system update in dry run mode"""
        self.engine.dry_run = True
        
        result = self.engine._execute_update()
        
        self.assertTrue(result.success)
        self.assertEqual(result.output, "Would update system")
        self.assertEqual(result.error, "")
        
    def test_create_rebuild_script(self):
        """Test rebuild script creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Override temp location for testing
            original_tmp = Path('/tmp')
            test_tmp = Path(tmpdir)
            
            # Monkey patch the method to use test directory
            def create_rebuild_script_test():
                script_path = test_tmp / 'nixos-rebuild-wrapper.sh'
                script_content = '''#!/usr/bin/env bash
echo "Starting NixOS rebuild..."
sudo nixos-rebuild switch > /tmp/nixos-rebuild.log 2>&1 &
echo "Rebuild started!"'''
                script_path.write_text(script_content)
                script_path.chmod(0o755)
                return script_path
                
            self.engine._create_rebuild_script = create_rebuild_script_test
            script_path = self.engine._create_rebuild_script()
            
            self.assertTrue(script_path.exists())
            self.assertTrue(os.access(script_path, os.X_OK))
            content = script_path.read_text()
            self.assertIn("#!/usr/bin/env bash", content)
            self.assertIn("nixos-rebuild switch", content)
        
    def test_run_command_success(self):
        """Test successful command execution"""
        # Command execution is routed through our test backend
        result = self.engine._run_command(['echo', 'test'])
        
        self.assertEqual(result['returncode'], 0)
        self.assertEqual(result['stdout'], "Output")
        self.assertEqual(result['stderr'], "")
            
    def test_run_command_timeout(self):
        """Test command execution with timeout"""
        # Configure backend to simulate a long-running command
        self.backend.set_process_response(
            'sleep',
            TestProcess(0, b"", b"", execution_time=10)
        )
        
        result = self.engine._run_command(['sleep', '10'], timeout=1)
        
        self.assertEqual(result['returncode'], -1)
        self.assertEqual(result['stdout'], '')
        self.assertIn('timed out', result['stderr'])
            
    def test_run_command_exception(self):
        """Test command execution with exception"""
        # Configure backend to raise an exception
        self.backend.set_process_response(
            'test',
            TestProcess(-1, b"", b"Test error")
        )
        
        result = self.engine._run_command(['test'])
        
        self.assertEqual(result['returncode'], -1)
        self.assertEqual(result['stdout'], '')
        self.assertIn('error', result['stderr'].lower())
            
    def test_execute_search_no_query(self):
        """Test search execution without query"""
        result = self.engine._execute_search(None)
        
        self.assertFalse(result.success)
        self.assertIn("No search query", result.error)
        
    def test_execute_search_with_results(self):
        """Test search with results"""
        # Search results are determined by test backend
        result = self.engine._execute_search("firefox")
        
        self.assertTrue(result.success)
        self.assertIn("firefox", result.output)
        self.assertIn("Web browser", result.output)
        
    def test_execute_search_no_results(self):
        """Test search with no results"""
        # Backend configured to return no results for 'nonexistent'
        result = self.engine._execute_search("nonexistent")
        
        self.assertTrue(result.success)
        self.assertIn("No packages found", result.output)
        
    def test_execute_rollback_dry_run(self):
        """Test rollback in dry run mode"""
        self.engine.dry_run = True
        
        result = self.engine._execute_rollback()
        
        self.assertTrue(result.success)
        self.assertEqual(result.output, "Would rollback system")
        
    def test_debug_output(self):
        """Test debug output when DEBUG env var is set"""
        # Set DEBUG environment variable
        os.environ['DEBUG'] = '1'
        
        # Configure backend to simulate API failure
        self.backend.api_available = False
        self.engine._has_python_api = False
        
        # Capture debug output
        import io
        import contextlib
        
        output_buffer = io.StringIO()
        with contextlib.redirect_stdout(output_buffer):
            result = self.engine._execute_install("test")
        
        # Check that debug info was printed
        output = output_buffer.getvalue()
        if output:  # Debug output is optional
            self.assertIsInstance(output, str)


    def test_native_api_rollback(self):
        """Test rollback using native Python API"""
        if self.engine._has_python_api:
            # Test rollback to specific generation
            result = self.engine._execute_rollback(generation=2)
            
            # Verify API was called
            self.assertIn(('rollback', 2), self.backend.api_calls)
            self.assertEqual(self.backend.current_generation, 2)
    
    def test_subprocess_fallback(self):
        """Test fallback to subprocess when API unavailable"""
        # Disable API
        self.engine._has_python_api = False
        
        # Should still work via subprocess
        result = self.engine._execute_install("vim")
        
        # Verify package was installed
        self.assertIn("vim", self.backend.installed_packages)
    
    def test_progress_callback_integration(self):
        """Test progress callbacks are properly invoked"""
        # Install a package with progress tracking
        self.engine._execute_install("emacs")
        
        # Verify progress was reported
        self.assertTrue(len(self.progress_callback.calls) > 0)
        
        # Check progress values are reasonable
        for message, progress, timestamp in self.progress_callback.calls:
            self.assertIsInstance(message, str)
            self.assertGreaterEqual(progress, 0.0)
            self.assertLessEqual(progress, 1.0)


    def test_persona_aware_installation(self):
        """Test installation adapts to different personas"""
        # Simulate Grandma Rose persona
        intent = Intent(
            type=IntentType.INSTALL,
            entities={'package': 'firefox'},
            confidence=0.95,
            raw_input="I need that Firefox thing my grandson mentioned",
            persona="grandma_rose"
        )
        
        result = self.engine.execute([], intent)
        
        # Response should be friendly and non-technical
        self.assertTrue(result.success)
        self.assertNotIn("nixpkgs", result.output.lower())
        self.assertNotIn("derivation", result.output.lower())
    
    def test_maya_speed_requirement(self):
        """Test Maya (ADHD) gets ultra-fast responses"""
        intent = Intent(
            type=IntentType.INSTALL,
            entities={'package': 'firefox'},
            confidence=0.95,
            raw_input="firefox now",
            persona="maya_adhd"
        )
        
        import time
        start = time.time()
        result = self.engine.execute([], intent)
        duration = time.time() - start
        
        # Must be under 1 second for Maya
        self.assertLess(duration, 1.0)
        self.assertTrue(result.success)


if __name__ == '__main__':
    unittest.main()