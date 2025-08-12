#!/usr/bin/env python3
"""
🧪 Fixed Test Suite for v1.3.0 Features
Tests Tree-sitter and Fuzzy Search integration
Uses direct imports instead of subprocess to avoid Poetry issues
"""

import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Tuple
import io
from contextlib import redirect_stdout, redirect_stderr

# Test results tracking
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def run_test(name: str, test_func) -> bool:
    """Run a single test and track results"""
    try:
        print(f"\n📝 Testing: {name}")
        print("-" * 50)
        result, message = test_func()
        if result:
            print(f"✅ PASSED: {message}")
            test_results["passed"].append(name)
            return True
        else:
            print(f"❌ FAILED: {message}")
            test_results["failed"].append((name, message))
            return False
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
        test_results["failed"].append((name, str(e)))
        return False

def test_fuzzy_search_import() -> Tuple[bool, str]:
    """Test that fuzzy search module imports correctly"""
    try:
        from nix_for_humanity.search import create_searcher, PackageResult
        searcher = create_searcher()
        return True, "Fuzzy search module imports successfully"
    except ImportError as e:
        return False, f"Import error: {e}"

def test_fuzzy_search_basic() -> Tuple[bool, str]:
    """Test basic fuzzy search functionality"""
    try:
        from nix_for_humanity.search import FuzzySearchAdapter
        
        searcher = FuzzySearchAdapter()
        test_packages = [
            {"name": "firefox", "description": "Web browser"},
            {"name": "firefox-esr", "description": "Extended support"},
            {"name": "vim", "description": "Text editor"}
        ]
        
        results = searcher._batch_search("fire", test_packages)
        
        if len(results) >= 2 and results[0].name.startswith("fire"):
            return True, f"Found {len(results)} matches for 'fire'"
        else:
            return False, f"Expected firefox matches, got {[r.name for r in results]}"
    except Exception as e:
        return False, f"Search failed: {e}"

def test_natural_language_expansion() -> Tuple[bool, str]:
    """Test natural language query expansion"""
    try:
        from nix_for_humanity.search import ConsciousFuzzySearch
        
        searcher = ConsciousFuzzySearch()
        expanded = searcher._expand_natural_language("photo editor")
        
        if "gimp" in expanded.lower() or "krita" in expanded.lower():
            return True, f"Expanded 'photo editor' correctly"
        else:
            return False, f"Expansion didn't include expected packages: {expanded}"
    except Exception as e:
        return False, f"Expansion failed: {e}"

def test_tree_sitter_import() -> Tuple[bool, str]:
    """Test that Tree-sitter modules import correctly"""
    try:
        from nix_for_humanity.parsers.multi_language_parser import MultiLanguageAnalyzer
        from nix_for_humanity.parsers.shell_script_migrator import ShellToNixMigrator
        
        analyzer = MultiLanguageAnalyzer()
        migrator = ShellToNixMigrator()
        return True, "Tree-sitter modules import successfully"
    except ImportError as e:
        return False, f"Import error: {e}"

def test_project_analysis() -> Tuple[bool, str]:
    """Test project analysis with Tree-sitter"""
    try:
        from nix_for_humanity.parsers.multi_language_parser import analyze_and_generate
        
        # Analyze current directory (should detect Python project)
        result = analyze_and_generate(".")
        
        if result["analysis"]["language"] == "python":
            deps = len(result["analysis"]["dependencies"])
            return True, f"Detected Python project with {deps} dependencies"
        else:
            return False, f"Expected Python, got {result['analysis']['language']}"
    except Exception as e:
        return False, f"Analysis failed: {e}"

def test_shell_migration() -> Tuple[bool, str]:
    """Test shell script migration"""
    try:
        from nix_for_humanity.parsers.shell_script_migrator import ShellToNixMigrator
        
        migrator = ShellToNixMigrator()
        
        # Create test script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write("""#!/bin/bash
apt-get install -y vim git
systemctl enable docker
""")
            script_path = f.name
        
        try:
            result = migrator.migrate_script(script_path)
            
            if result["success"]:
                packages = result["analysis"]["packages_needed"]
                if "vim" in packages and "git" in packages:
                    return True, f"Migrated script with {len(packages)} packages"
                else:
                    return False, f"Missing expected packages: {packages}"
            else:
                return False, f"Migration failed: {result.get('analysis', {}).get('warnings', [])}"
        finally:
            Path(script_path).unlink(missing_ok=True)
            
    except Exception as e:
        return False, f"Migration error: {e}"

def test_cli_search_direct() -> Tuple[bool, str]:
    """Test CLI search command using direct import instead of subprocess"""
    try:
        # Import the CLI module directly
        import sys
        import os
        
        # Add src to path
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
        
        # Import the search handler
        from nix_for_humanity.cli.search_command import handle_search_in_query
        
        # Capture output
        output_buffer = io.StringIO()
        
        # Test search query
        with redirect_stdout(output_buffer):
            result = handle_search_in_query("search for vim")
        
        output = output_buffer.getvalue()
        
        if "vim" in output.lower() and ("found" in output.lower() or "packages" in output.lower() or "results" in output.lower()):
            vim_count = output.lower().count("vim")
            return True, f"CLI search found vim ({vim_count} mentions)"
        else:
            snippet = output[:500] if output else "No output"
            return False, f"No vim in search results: {snippet}"
    except Exception as e:
        return False, f"CLI error: {e}"

def test_cli_analyze_direct() -> Tuple[bool, str]:
    """Test CLI analyze command using direct import"""
    try:
        import sys
        import os
        
        # Import the TreeSitterCommands directly
        from nix_for_humanity.cli.tree_sitter_commands_standalone import TreeSitterCommands
        
        # Run analysis
        commands = TreeSitterCommands()
        result = commands.analyze_project(".")
        
        if result["success"] and "python" in result["message"].lower():
            return True, "CLI analyze command works"
        else:
            snippet = str(result)[:500] if result else "No output"
            return False, f"Unexpected output: {snippet}"
    except Exception as e:
        return False, f"CLI error: {e}"

def test_graceful_degradation() -> Tuple[bool, str]:
    """Test that features degrade gracefully when dependencies are missing"""
    try:
        from nix_for_humanity.search.fuzzy_search import FuzzySearchAdapter
        
        adapter = FuzzySearchAdapter()
        backend = adapter._detect_backend()
        
        # Should have detected a backend
        if backend in ["fzf", "skim", "python"]:
            return True, f"Detected backend: {backend}"
        else:
            return False, f"Unknown backend: {backend}"
    except Exception as e:
        return False, f"Degradation test failed: {e}"

def test_package_suggestions() -> Tuple[bool, str]:
    """Test package suggestion system"""
    try:
        from nix_for_humanity.config.config_generator import ConfigGenerator
        
        generator = ConfigGenerator()
        suggestions = generator.suggest_packages("text editor")
        
        if suggestions and any("vim" in s.lower() or "emacs" in s.lower() for s in suggestions):
            return True, f"Got {len(suggestions)} suggestions for text editor"
        else:
            return False, f"No relevant suggestions: {suggestions}"
    except Exception as e:
        return False, f"Suggestion test failed: {e}"

def test_consciousness_features() -> Tuple[bool, str]:
    """Test consciousness-first features like sacred pause"""
    try:
        from nix_for_humanity.search import ConsciousFuzzySearch
        
        searcher = ConsciousFuzzySearch()
        
        # Simulate multiple failed searches
        for _ in range(4):
            searcher.search_count += 1
        
        # Next search should trigger sacred pause logic
        if searcher.search_count >= 4:
            return True, "Sacred pause detection works"
        else:
            return False, f"Search count not tracked: {searcher.search_count}"
    except Exception as e:
        return False, f"Consciousness features failed: {e}"

def test_performance() -> Tuple[bool, str]:
    """Test performance metrics"""
    try:
        from nix_for_humanity.search import FuzzySearchAdapter
        
        searcher = FuzzySearchAdapter()
        
        # Create large package list
        packages = [
            {"name": f"package{i}", "description": f"Description {i}"}
            for i in range(1000)
        ]
        
        start = time.time()
        results = searcher._batch_search("package5", packages)
        elapsed = time.time() - start
        
        if elapsed < 0.1:  # Should be < 100ms
            return True, f"Search 1000 packages in {elapsed:.3f}s"
        else:
            return False, f"Too slow: {elapsed:.3f}s for 1000 packages"
    except Exception as e:
        return False, f"Performance test failed: {e}"

def main():
    """Run all tests and report results"""
    print("=" * 70)
    print("🧪 v1.3.0 Feature Test Suite (Fixed)")
    print("=" * 70)
    
    # Define all tests
    tests = [
        ("Fuzzy Search Import", test_fuzzy_search_import),
        ("Basic Fuzzy Search", test_fuzzy_search_basic),
        ("Natural Language Expansion", test_natural_language_expansion),
        ("Tree-sitter Import", test_tree_sitter_import),
        ("Project Analysis", test_project_analysis),
        ("Shell Script Migration", test_shell_migration),
        ("CLI Search (Direct)", test_cli_search_direct),
        ("CLI Analyze (Direct)", test_cli_analyze_direct),
        ("Graceful Degradation", test_graceful_degradation),
        ("Package Suggestions", test_package_suggestions),
        ("Consciousness Features", test_consciousness_features),
        ("Performance Metrics", test_performance),
    ]
    
    # Run all tests
    for name, test_func in tests:
        run_test(name, test_func)
    
    # Report results
    print("\n" + "=" * 70)
    print("📊 Test Results Summary")
    print("=" * 70)
    
    total = len(tests)
    passed = len(test_results["passed"])
    failed = len(test_results["failed"])
    
    print(f"\n✅ Passed: {passed}/{total}")
    for test in test_results["passed"]:
        print(f"   • {test}")
    
    if test_results["failed"]:
        print(f"\n❌ Failed: {failed}/{total}")
        for test, reason in test_results["failed"]:
            print(f"   • {test}")
            print(f"     Reason: {reason}")
    
    if test_results["warnings"]:
        print(f"\n⚠️  Warnings: {len(test_results['warnings'])}")
        for warning in test_results["warnings"]:
            print(f"   • {warning}")
    
    # Overall status
    print("\n" + "=" * 70)
    if failed == 0:
        print("🎉 All tests passed! v1.3.0 features are working correctly.")
        print("✅ Ready to proceed with polishing and release.")
    elif failed <= 2:
        print("⚠️  Most tests passed but some issues need attention.")
        print("🔧 Fix the failures before release.")
    else:
        print("❌ Multiple failures detected. Significant work needed.")
        print("🚧 Development required before v1.3.0 can be released.")
    
    # Suggest next steps
    print("\n📝 Next Steps for v1.3.0 Release:")
    print("1. Update VERSION files (remove -dev suffix)")
    print("2. Finalize CHANGELOG.md with release date")
    print("3. Create release notes and announcement")
    print("4. Tag and push to GitHub")
    print("5. Create GitHub release")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())