#!/usr/bin/env python3
"""
Quick test script for Python backend functionality
Run this to verify the backend is working correctly
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from nixos_integration import NixForHumanityBackend, NixOSPythonBackend


async def test_basic_functionality():
    """Test basic backend functionality"""
    print("🧪 Testing Nix for Humanity Python Backend\n")

    # Test 1: Backend initialization
    print("1️⃣ Testing backend initialization...")
    try:
        backend = NixOSPythonBackend()
        print("   ✅ Backend initialized")
        print(f"   📊 Python API available: {backend.has_python_api}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return

    # Test 2: System info
    print("\n2️⃣ Testing system info retrieval...")
    try:
        info = await backend.get_system_info()
        print("   ✅ System info retrieved:")
        print(f"      NixOS Version: {info.get('nixos_version', 'unknown')}")
        print(f"      Current Generation: {info.get('current_generation', 'unknown')}")
        print(f"      Has Python API: {info.get('has_python_api', False)}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test 3: Package search
    print("\n3️⃣ Testing package search...")
    try:
        packages = await backend.search_packages("hello")
        print(f"   ✅ Found {len(packages)} packages")
        if packages:
            pkg = packages[0]
            print(f"      Example: {pkg['name']} ({pkg['version']})")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test 4: Natural language processing
    print("\n4️⃣ Testing natural language integration...")
    try:
        nfh_backend = NixForHumanityBackend()

        # Test intent extraction
        queries = [
            "install firefox",
            "search for python",
            "update my system",
            "how do I rollback?",
        ]

        for query in queries:
            result = await nfh_backend.process_natural_language(query, execute=False)
            print(f"   Query: '{query}'")
            print("   ✅ Processed successfully")
            if "explanation" in result:
                print(f"      Response: {result['explanation'][:100]}...")
            elif "message" in result:
                print(f"      Response: {result['message']}")
            print()

    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test 5: Progress callbacks
    print("\n5️⃣ Testing progress callbacks...")
    try:
        progress_updates = []

        def track_progress(msg, pct):
            progress_updates.append((msg, pct))

        backend.add_progress_callback(track_progress)

        # Do a quick search to trigger progress
        await backend.search_packages("test")

        if progress_updates:
            print(f"   ✅ Progress tracking works ({len(progress_updates)} updates)")
        else:
            print("   ⚠️  No progress updates captured")

    except Exception as e:
        print(f"   ❌ Failed: {e}")

    print("\n✨ Testing complete!")


async def interactive_test():
    """Interactive test mode"""
    print("🗣️  Interactive Test Mode")
    print("Commands: search <query>, install <package>, status, quit\n")

    backend = NixForHumanityBackend()

    while True:
        try:
            cmd = input("test> ").strip()

            if cmd == "quit":
                break
            if cmd == "status":
                info = await backend.get_system_status()
                for key, value in info.items():
                    print(f"  {key}: {value}")
            elif cmd.startswith("search "):
                query = cmd[7:]
                packages = await backend.nixos_backend.search_packages(query)
                print(f"Found {len(packages)} packages:")
                for pkg in packages[:5]:
                    print(f"  - {pkg['name']} ({pkg['version']})")
            elif cmd.startswith("install "):
                package = cmd[8:]
                print(f"Would install: {package}")
                print("(Add --real flag to actually install)")
            else:
                # Try natural language
                result = await backend.process_natural_language(cmd)
                print(result.get("message", str(result)))

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print("\nGoodbye!")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Test Python backend")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run interactive test"
    )

    args = parser.parse_args()

    if args.interactive:
        asyncio.run(interactive_test())
    else:
        asyncio.run(test_basic_functionality())


if __name__ == "__main__":
    main()
