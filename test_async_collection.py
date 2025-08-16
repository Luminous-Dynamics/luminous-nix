#!/usr/bin/env python3
"""
Test async system collection without full environmental awareness.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from luminous_nix.environmental.async_system_collector import (
    get_nixos_collector,
    get_service_collector,
    get_package_collector,
    collect_full_system_state
)


async def test_nixos_collection():
    """Test NixOS state collection"""
    print("🖥️  Testing NixOS Collection...")
    
    collector = get_nixos_collector()
    
    # Test individual methods
    version = await collector.get_nixos_version()
    print(f"  Version: {version}")
    
    generation = await collector.get_current_generation()
    print(f"  Current Generation: {generation}")
    
    generations = await collector.get_available_generations()
    print(f"  Available Generations: {generations[:5] if generations else 'None'}")
    
    channels = await collector.get_channels()
    print(f"  Channels: {len(channels)} configured")
    for channel in channels[:2]:
        print(f"    - {channel.get('name', 'unknown')}: {channel.get('url', 'unknown')[:50]}...")
    
    # Test full collection
    print("\n  Testing full collection...")
    data = await collector.collect_all()
    print(f"  ✅ Collected all NixOS state: {len(data)} fields")


async def test_service_collection():
    """Test service state collection"""
    print("\n🔧 Testing Service Collection...")
    
    collector = get_service_collector()
    
    # Test single service
    nix_daemon = await collector.get_service_status('nix-daemon')
    print(f"  nix-daemon: {nix_daemon['status']}")
    
    # Test key services
    services = await collector.get_key_services()
    print(f"  Collected {len(services)} key services")
    for service in services:
        icon = "🟢" if service['status'] == 'active' else "🔴"
        print(f"    {icon} {service['name']}: {service['status']}")


async def test_package_collection():
    """Test package collection"""
    print("\n📦 Testing Package Collection...")
    
    collector = get_package_collector()
    
    count = await collector.get_installed_package_count()
    print(f"  Installed packages: {count}")
    
    recent = await collector.get_recent_packages()
    if recent:
        print(f"  Recent packages:")
        for pkg in recent:
            print(f"    - {pkg}")
    else:
        print("  No recent packages found")


async def test_full_collection():
    """Test complete system state collection"""
    print("\n🌟 Testing Full System Collection...")
    
    state = await collect_full_system_state()
    
    print(f"  NixOS version: {state['nixos'].get('version', 'unknown')}")
    print(f"  Services monitored: {len(state['services'])}")
    print(f"  Packages installed: {state['package_count']}")
    
    # Save to file
    output_file = Path('/tmp/system_state.json')
    with open(output_file, 'w') as f:
        # Convert to serializable format
        serializable = {
            'nixos': state['nixos'],
            'services': state['services'],
            'package_count': state['package_count'],
            'recent_packages': state['recent_packages']
        }
        json.dump(serializable, f, indent=2)
    
    print(f"\n  📸 State saved to: {output_file}")


async def main():
    """Main test function"""
    print("🚀 Luminous Nix - Async System Collection Test\n")
    
    try:
        # Run all tests
        await test_nixos_collection()
        await test_service_collection()
        await test_package_collection()
        await test_full_collection()
        
        print("\n✅ All async collection tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())