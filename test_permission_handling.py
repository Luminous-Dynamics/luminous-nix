#!/usr/bin/env python3
"""
Test and demonstrate graceful permission handling for healing operations.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from luminous_nix.self_healing.permission_handler import (
    PermissionHandler,
    GracefulHealingAdapter,
    check_capabilities
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_capabilities():
    """Test what capabilities are available"""
    print("\n" + "="*70)
    print("🔍 CHECKING SYSTEM CAPABILITIES")
    print("="*70)
    
    capabilities = check_capabilities()
    
    print("\n📊 Permission Status")
    print("-"*40)
    print(f"Sudo available: {'✅' if capabilities['sudo_available'] else '❌'}")
    print(f"Passwordless sudo: {'✅' if capabilities['passwordless_sudo'] else '❌'}")
    print(f"Can execute privileged: {'✅' if capabilities['can_execute_privileged'] else '❌'}")
    
    print("\n✅ Unprivileged Operations (work without root):")
    for op in capabilities['unprivileged_capabilities']:
        print(f"  - {op}")
    
    print("\n⚠️ Privileged Operations (need root):")
    for op in capabilities['requires_privileges']:
        print(f"  - {op}")
    
    return capabilities


async def test_unprivileged_operations():
    """Test operations that don't need root"""
    print("\n" + "="*70)
    print("🟢 TESTING UNPRIVILEGED OPERATIONS")
    print("="*70)
    
    handler = PermissionHandler()
    
    # Test reading system info
    print("\n📖 Reading system information...")
    result = await handler.execute_command(
        ['uname', '-a'],
        operation_type='read_system_info',
        require_root=False
    )
    
    if result['success']:
        print(f"✅ System info: {result['output'].strip()}")
        print(f"   Method used: {result['method']}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test checking disk usage
    print("\n💾 Checking disk usage...")
    result = await handler.execute_command(
        ['df', '-h', '/'],
        operation_type='check_disk_usage',
        require_root=False
    )
    
    if result['success']:
        lines = result['output'].strip().split('\n')
        if len(lines) > 1:
            print(f"✅ Root filesystem: {lines[1]}")
        print(f"   Method used: {result['method']}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test process listing
    print("\n📋 Listing processes...")
    result = await handler.execute_command(
        ['ps', 'aux'],
        operation_type='list_processes',
        require_root=False
    )
    
    if result['success']:
        lines = result['output'].strip().split('\n')
        print(f"✅ Found {len(lines)-1} processes")
        print(f"   Method used: {result['method']}")
    else:
        print(f"❌ Failed: {result['error']}")


async def test_privileged_operations():
    """Test operations that need root"""
    print("\n" + "="*70)
    print("🔴 TESTING PRIVILEGED OPERATIONS")
    print("="*70)
    
    adapter = GracefulHealingAdapter()
    
    # Test service restart (will fail or prompt for password)
    print("\n🔄 Testing service restart...")
    print("   (This will fail gracefully or prompt for sudo)")
    
    result = await adapter.restart_service('non-existent-service')
    
    if result['success']:
        print(f"✅ Service operation completed")
        print(f"   Method: {result['method']}")
    else:
        print(f"ℹ️ As expected, privileged operation failed gracefully")
        print(f"   Method attempted: {result.get('method', 'none')}")
        if 'suggestion' in result:
            print(f"   💡 Suggestion: {result['suggestion']}")
    
    # Test CPU governor change
    print("\n⚡ Testing CPU governor change...")
    print("   (This requires root privileges)")
    
    result = await adapter.set_cpu_governor('ondemand')
    
    if result['success']:
        print(f"✅ CPU governor changed")
        print(f"   Method: {result['method']}")
    else:
        print(f"ℹ️ CPU governor change requires privileges")
        print(f"   Method attempted: {result.get('method', 'none')}")
        if 'suggestion' in result:
            print(f"   💡 Suggestion: {result['suggestion']}")
    
    # Test cache clearing
    print("\n🧹 Testing cache clearing...")
    print("   (Will try system cache, then fall back to user cache)")
    
    result = await adapter.clear_caches()
    
    if result['success']:
        print(f"✅ Caches cleared")
        print(f"   Method: {result['method']}")
        if result['method'] == 'user_space_fallback':
            print(f"   ℹ️ Only user caches were cleared (no root)")
    else:
        print(f"❌ Cache clearing failed")
        print(f"   Error: {result.get('error', 'Unknown')}")


async def test_fallback_strategies():
    """Test fallback strategies for operations"""
    print("\n" + "="*70)
    print("🔄 TESTING FALLBACK STRATEGIES")
    print("="*70)
    
    handler = PermissionHandler()
    
    # Register a custom fallback
    async def custom_service_restart_fallback(command):
        print("   🔧 Using custom fallback: sending signal to user service")
        # Simulate a user-space alternative
        return {
            'success': True,
            'output': 'User service signaled',
            'method': 'custom_fallback'
        }
    
    handler.register_fallback('restart_service', custom_service_restart_fallback)
    
    print("\n📝 Registered custom fallback for service restart")
    
    # Test with fallback
    result = await handler.execute_command(
        ['systemctl', 'restart', 'test-service'],
        operation_type='restart_service',
        require_root=True
    )
    
    if result['success']:
        print(f"✅ Operation succeeded via fallback")
        print(f"   Method: {result['method']}")
        print(f"   Output: {result['output']}")


async def main():
    """Run all permission handling tests"""
    print("\n" + "="*70)
    print("🔐 LUMINOUS NIX PERMISSION HANDLING TEST")
    print("="*70)
    
    # Check capabilities
    capabilities = await test_capabilities()
    
    # Test unprivileged operations
    await test_unprivileged_operations()
    
    # Test privileged operations
    await test_privileged_operations()
    
    # Test fallback strategies
    await test_fallback_strategies()
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    print("\n🎯 Key Findings:")
    if capabilities['passwordless_sudo']:
        print("✅ System has passwordless sudo - all operations available")
    elif capabilities['sudo_available']:
        print("⚠️ Sudo available but requires password - limited automation")
    else:
        print("❌ No sudo available - only unprivileged operations work")
    
    print("\n💡 Recommendations:")
    if not capabilities['passwordless_sudo'] and capabilities['sudo_available']:
        print("1. For development, consider adding passwordless sudo for specific commands:")
        print("   echo '$(whoami) ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart *' | sudo tee /etc/sudoers.d/luminous-healing")
        print("   echo '$(whoami) ALL=(ALL) NOPASSWD: /usr/bin/cpupower' | sudo tee -a /etc/sudoers.d/luminous-healing")
    
    print("\n2. For production, implement the SystemD service approach:")
    print("   - See docs/PERMISSION_HANDLING_STRATEGY.md")
    
    print("\n3. The system works gracefully without privileges:")
    print("   - Monitoring and detection always work")
    print("   - Backups are created in user directories")
    print("   - Healing plans are generated (even if not executable)")
    print("   - Metrics are exposed for external monitoring")


if __name__ == "__main__":
    asyncio.run(main())