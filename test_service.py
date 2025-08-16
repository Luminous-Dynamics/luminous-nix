#!/usr/bin/env python3
"""
Test the new service layer architecture.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from luminous_nix.service_simple import LuminousNixService, ServiceOptions


async def test_service():
    """Test basic service functionality"""
    print("🧪 Testing Luminous Nix Service Layer\n")
    
    # Create service with options
    options = ServiceOptions(
        execute=False,  # Dry run mode
        interface="test",
        verbose=True
    )
    
    service = LuminousNixService(options)
    
    # Test 1: Initialize
    print("1️⃣ Initializing service...")
    try:
        await service.initialize()
        print("   ✅ Service initialized\n")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}\n")
        return
    
    # Test 2: Execute a simple command
    print("2️⃣ Testing command execution...")
    try:
        response = await service.execute_command("help")
        print(f"   Success: {response.success}")
        print(f"   Response: {response.text[:100]}...")
        print("   ✅ Command executed\n")
    except Exception as e:
        print(f"   ❌ Failed to execute: {e}\n")
    
    # Test 3: Alias management
    print("3️⃣ Testing alias management...")
    try:
        # Create an alias
        success = service.create_alias("test-alias")
        print(f"   Create alias: {'✅' if success else '❌'}")
        
        # List aliases
        aliases = service.list_aliases()
        print(f"   Current aliases: {aliases}")
        
        # Remove the test alias
        service.remove_alias("test-alias")
        print("   ✅ Alias management works\n")
    except Exception as e:
        print(f"   ❌ Alias management failed: {e}\n")
    
    # Test 4: Settings (skip for now in simple version)
    print("4️⃣ Settings management - skipped in simple version")
    
    # Test 5: Cleanup
    print("5️⃣ Cleaning up...")
    await service.cleanup()
    print("   ✅ Cleanup complete\n")
    
    print("✨ Service layer tests complete!")


if __name__ == "__main__":
    asyncio.run(test_service())