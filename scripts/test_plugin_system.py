#!/usr/bin/env python3
"""
Test script to demonstrate the plugin system
"""

import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.plugin_manager import get_plugin_manager


def main():
    """Test the plugin system"""
    print("🔌 Testing Nix for Humanity Plugin System\n")
    print("=" * 50)
    
    # Get plugin manager
    manager = get_plugin_manager()
    
    # Load plugins
    print("\n📦 Loading plugins...")
    if manager.load_all_plugins():
        print("✅ Plugins loaded successfully!")
    else:
        print("⚠️  Some plugins failed to load")
    
    # Show loaded plugins
    info = manager.get_plugin_info()
    print(f"\n📊 Loaded {info['total_plugins']} plugins:")
    print(f"  - Personality plugins: {info['personality_plugins']}")
    print(f"  - Feature plugins: {info['feature_plugins']}")
    
    print("\n🔍 Plugin Details:")
    for name, plugin_info in info['plugins'].items():
        print(f"\n  • {name} (v{plugin_info['version']})")
        print(f"    {plugin_info['description']}")
        print(f"    Capabilities: {', '.join(plugin_info['capabilities'])}")
    
    # Test personality transformations
    print("\n\n🎭 Testing Personality Transformations")
    print("=" * 50)
    
    base_response = "To install firefox, use: nix-env -iA nixos.firefox"
    
    personalities = ['minimal', 'friendly']
    for personality in personalities:
        print(f"\n### {personality.title()} Personality:")
        manager.set_personality(personality)
        transformed = manager.apply_personality(base_response)
        print(f"{transformed}")
    
    # Test intent handling
    print("\n\n🎯 Testing Intent Handling")
    print("=" * 50)
    
    # Test search
    print("\n### Search Intent:")
    search_result = manager.handle_intent('search_package', {
        'query': 'search for firefox',
        'package': 'firefox'
    })
    
    if search_result:
        print(f"Success: {search_result['success']}")
        print(f"Response preview: {search_result['response'][:200]}...")
    else:
        print("No handler found for search_package")
    
    # Test install instructions
    print("\n### Install Instructions Intent:")
    install_result = manager.handle_intent('install_package', {
        'package': 'firefox',
        'execute': False
    })
    
    if install_result:
        print(f"Success: {install_result['success']}")
        print(f"Response preview: {install_result['response'][:200]}...")
    else:
        print("No handler found for install_package")
    
    # Show metrics
    print("\n\n📈 Plugin Metrics")
    print("=" * 50)
    metrics = manager.get_metrics()
    for plugin_name, plugin_metrics in metrics.items():
        print(f"\n{plugin_name}:")
        for key, value in plugin_metrics.items():
            print(f"  {key}: {value}")
    
    print("\n\n✅ Plugin system test complete!")


if __name__ == "__main__":
    main()