#!/usr/bin/env python3
"""
Test the service layer with minimal backend interaction.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


async def test_minimal():
    """Test basic service layer functionality without full backend"""
    print("🧪 Testing Luminous Nix Service Layer (Minimal)\n")
    
    # Test imports
    print("1️⃣ Testing imports...")
    try:
        from luminous_nix.service_simple import LuminousNixService, ServiceOptions
        print("   ✅ Service imports successful\n")
    except Exception as e:
        print(f"   ❌ Import failed: {e}\n")
        return
    
    # Test service creation
    print("2️⃣ Creating service...")
    try:
        options = ServiceOptions(
            execute=False,  # Dry run mode
            interface="test",
            verbose=True
        )
        service = LuminousNixService(options)
        print("   ✅ Service created\n")
    except Exception as e:
        print(f"   ❌ Service creation failed: {e}\n")
        return
    
    # Test alias management (no backend needed)
    print("3️⃣ Testing alias management...")
    try:
        # Create an alias
        success = service.create_alias("luminix")
        print(f"   Create alias 'luminix': {'✅' if success else '❌'}")
        
        # List aliases
        aliases = service.list_aliases()
        print(f"   Current aliases: {aliases}")
        
        # Create another alias
        service.create_alias("lnix")
        aliases = service.list_aliases()
        print(f"   After adding 'lnix': {aliases}")
        
        # Remove an alias
        service.remove_alias("lnix")
        aliases = service.list_aliases()
        print(f"   After removing 'lnix': {aliases}")
        print("   ✅ Alias management works\n")
    except Exception as e:
        print(f"   ❌ Alias management failed: {e}\n")
    
    print("✨ Minimal service layer tests complete!")
    print("\n📝 Note: Full backend initialization requires database setup.")
    print("   For production use, ensure the nixos_knowledge.db exists.")


if __name__ == "__main__":
    asyncio.run(test_minimal())