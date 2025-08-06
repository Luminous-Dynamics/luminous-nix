#!/usr/bin/env python3
"""
Run accessibility tests for Nix for Humanity
Validates screen reader support, WCAG compliance, and persona accessibility
"""

import sys
import os
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_tests():
    """Run all accessibility tests"""
    print("🧪 Running Nix for Humanity Accessibility Tests\n")
    
    # Test categories
    test_suites = [
        {
            'name': 'Screen Reader Compatibility',
            'pattern': 'tests/accessibility/test_screen_reader_compatibility.py',
            'description': 'Testing screen reader support for all components'
        },
        {
            'name': 'WCAG Compliance',
            'pattern': 'tests/accessibility/test_screen_reader_compatibility.py::TestWCAGCompliance',
            'description': 'Validating WCAG AAA compliance'
        },
        {
            'name': 'Persona Accessibility',
            'pattern': 'tests/accessibility/test_screen_reader_compatibility.py::TestPersonaAccessibility',
            'description': 'Testing accessibility for all 10 personas'
        },
        {
            'name': 'Keyboard Navigation',
            'pattern': 'tests/accessibility/test_screen_reader_compatibility.py::TestCLIScreenReaderSupport::test_keyboard_navigation',
            'description': 'Validating keyboard-only operation'
        }
    ]
    
    total_passed = 0
    total_failed = 0
    
    for suite in test_suites:
        print(f"\n{'='*60}")
        print(f"📋 {suite['name']}")
        print(f"   {suite['description']}")
        print('='*60)
        
        # Run the test suite
        cmd = [
            sys.executable, '-m', 'pytest',
            suite['pattern'],
            '-v',
            '--tb=short',
            '--color=yes'
        ]
        
        result = subprocess.run(cmd, cwd=project_root)
        
        if result.returncode == 0:
            print(f"✅ {suite['name']} PASSED")
            total_passed += 1
        else:
            print(f"❌ {suite['name']} FAILED")
            total_failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Accessibility Test Summary")
    print('='*60)
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"📈 Total: {total_passed + total_failed}")
    
    if total_failed == 0:
        print("\n🎉 All accessibility tests passed! The system is ready for all users.")
    else:
        print("\n⚠️  Some accessibility tests failed. Please fix these issues before deployment.")
        
    # Run coverage report for accessibility modules
    print(f"\n{'='*60}")
    print("📊 Accessibility Module Coverage")
    print('='*60)
    
    coverage_cmd = [
        sys.executable, '-m', 'pytest',
        'tests/accessibility/',
        '--cov=src/nix_for_humanity/accessibility',
        '--cov=src/nix_for_humanity/tui',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov/accessibility'
    ]
    
    subprocess.run(coverage_cmd, cwd=project_root)
    
    print("\n📁 Detailed coverage report available at: htmlcov/accessibility/index.html")
    
    return total_failed == 0


def validate_tui_accessibility():
    """Validate TUI components for accessibility"""
    print("\n🖥️  Validating TUI Accessibility...")
    
    # Check if all widgets have aria labels
    from src.nix_for_humanity.tui.accessible_widgets import (
        AccessibleButton,
        AccessibleInput,
        AccessibleList,
        AccessibleProgressBar,
        AccessibleNotification
    )
    
    widgets_ok = True
    
    # Test widget creation
    try:
        # Test button
        btn = AccessibleButton("Test", aria_label="Test button")
        assert hasattr(btn, 'aria_label')
        print("✅ AccessibleButton has aria_label support")
        
        # Test input
        inp = AccessibleInput(aria_label="Test input")
        assert hasattr(inp, 'screen_reader')
        print("✅ AccessibleInput has screen reader support")
        
        # Test list
        lst = AccessibleList(aria_label="Test list")
        assert hasattr(lst, 'announce_to_screen_reader')
        print("✅ AccessibleList has announcement support")
        
        # Test progress
        prog = AccessibleProgressBar(aria_label="Test progress")
        assert hasattr(prog, '_last_announced_percent')
        print("✅ AccessibleProgressBar has progress announcements")
        
        # Test notification
        notif = AccessibleNotification("Test", severity="info")
        assert hasattr(notif, 'severity')
        print("✅ AccessibleNotification has severity levels")
        
    except Exception as e:
        print(f"❌ Widget validation failed: {e}")
        widgets_ok = False
    
    return widgets_ok


def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n📦 Checking Dependencies...")
    
    required_packages = [
        'textual',
        'pytest',
        'pytest-cov',
        'pytest-asyncio'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        return False
    
    return True


def main():
    """Main entry point"""
    print("🌟 Nix for Humanity - Accessibility Validation Suite")
    print("="*60)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first.")
        return 1
    
    # Validate TUI components
    if not validate_tui_accessibility():
        print("\n❌ TUI accessibility validation failed.")
        return 1
    
    # Run tests
    if not run_tests():
        return 1
    
    print("\n✨ Accessibility validation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())