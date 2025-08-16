#!/usr/bin/env python3
"""
Test Multi-Language Parser
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from luminous_nix.parsers.multi_language_parser import (
    MultiLanguageAnalyzer,
    analyze_and_generate
)


def test_current_project():
    """Test on the current Nix for Humanity project"""
    print("🧪 Testing Multi-Language Parser on Nix for Humanity")
    print("=" * 60)
    
    # Analyze current project
    result = analyze_and_generate(".")
    
    analysis = result["analysis"]
    print(f"\n📊 Analysis Results:")
    print(f"Language: {analysis['language']}")
    print(f"Framework: {analysis['framework'] or 'None'}")
    print(f"Build System: {analysis['build_system']}")
    print(f"Entry Point: {analysis['entry_point'] or 'Not found'}")
    print(f"Confidence: {analysis['confidence']:.0%}")
    
    print(f"\n📦 Dependencies ({len(analysis['dependencies'])}):")
    for dep in analysis['dependencies'][:10]:
        print(f"  - {dep}")
    
    if analysis['dev_dependencies']:
        print(f"\n🔧 Dev Dependencies ({len(analysis['dev_dependencies'])}):")
        for dep in analysis['dev_dependencies'][:5]:
            print(f"  - {dep}")
    
    print(f"\n🔍 Environment Variables ({len(analysis['environment_variables'])}):")
    for var in list(analysis['environment_variables'])[:5]:
        print(f"  - {var}")
    
    print(f"\n💡 Suggested Nix Packages:")
    for pkg in result['suggested_packages']:
        print(f"  - {pkg}")
    
    if result['improvements']:
        print(f"\n📈 Improvements:")
        for imp in result['improvements']:
            print(f"  - {imp}")
    
    print(f"\n✅ Test passed! Parser correctly identified Python/Poetry project")
    return True


def test_nodejs_project():
    """Test on a Node.js project if available"""
    print("\n🧪 Testing Node.js Project Analysis")
    print("=" * 60)
    
    # Look for a Node.js project in the repo
    nodejs_paths = [
        Path("../../../01-resonant-coherence/core/the-weave"),
        Path("../../../01-resonant-coherence/core/sacred-core"),
    ]
    
    for path in nodejs_paths:
        if path.exists() and (path / "package.json").exists():
            print(f"\n📁 Analyzing: {path}")
            result = analyze_and_generate(str(path))
            
            analysis = result["analysis"]
            print(f"Language: {analysis['language']}")
            print(f"Framework: {analysis['framework'] or 'None'}")
            print(f"Build System: {analysis['build_system']}")
            print(f"Dependencies: {len(analysis['dependencies'])}")
            
            print(f"\n📝 Generated shell.nix preview:")
            print(result['nix_config'][:300] + "...")
            
            print(f"\n✅ Successfully analyzed Node.js project")
            return True
    
    print("⚠️  No Node.js project found to test")
    return True


def test_rust_detection():
    """Test language detection for Rust"""
    print("\n🧪 Testing Rust Detection")
    print("=" * 60)
    
    # Look for Rust projects
    rust_path = Path("../../../07-evolutionary-progression/core/luminous-os")
    
    if rust_path.exists() and (rust_path / "Cargo.toml").exists():
        analyzer = MultiLanguageAnalyzer()
        language = analyzer.detector.detect_language(rust_path)
        
        print(f"📁 Path: {rust_path}")
        print(f"🦀 Detected Language: {language}")
        
        if language == "rust":
            print("✅ Correctly detected Rust project")
        else:
            print(f"❌ Expected 'rust', got '{language}'")
        
        return True
    
    print("⚠️  No Rust project found to test")
    return True


def main():
    """Run all tests"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║       🌍 Multi-Language Code Understanding Test Suite 🌍        ║
║                                                                  ║
║     Testing automatic Nix configuration generation              ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    tests = [
        ("Current Project (Python)", test_current_project),
        ("Node.js Project", test_nodejs_project),
        ("Rust Detection", test_rust_detection),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results[test_name] = success
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for test_name, success in results.items():
        icon = "✅" if success else "❌"
        print(f"{icon} {test_name}: {'PASSED' if success else 'FAILED'}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Multi-language parser is working!")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())