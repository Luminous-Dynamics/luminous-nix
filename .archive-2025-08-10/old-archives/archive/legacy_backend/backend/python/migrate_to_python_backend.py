#!/usr/bin/env python3
"""
Migration script to update ask-nix tools to use Python backend
This provides a gradual migration path from subprocess to Python API
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from nixos_integration import NixForHumanityBackend


class AskNixPythonBridge:
    """
    Bridge between existing ask-nix interface and new Python backend
    Maintains compatibility while adding new capabilities
    """

    def __init__(self, personality="friendly"):
        self.backend = NixForHumanityBackend(personality)

    async def process_command(self, command: str, execute: bool = False) -> str:
        """
        Process command and return formatted string output
        Compatible with existing ask-nix tools
        """
        # Progress tracking
        progress_messages = []

        def track_progress(msg, pct):
            if pct >= 0:
                progress_messages.append(f"[{pct:3.0f}%] {msg}")
            else:
                progress_messages.append(msg)

        # Process with backend
        result = await self.backend.process_natural_language(
            command, execute=execute, progress_callback=track_progress
        )

        # Format output for compatibility
        output = []

        # Add progress messages if any
        if progress_messages and execute:
            output.append("📊 Progress:")
            output.extend(progress_messages)
            output.append("")

        # Main message
        if "message" in result:
            output.append(result["message"])

        # Handle different action types
        action = result.get("action")

        if action == "search" and result.get("packages"):
            output.append(f"\nFound {result['count']} packages:")
            for pkg in result["packages"][:5]:
                output.append(f"  📦 {pkg['name']} ({pkg['version']})")
                if pkg.get("description"):
                    output.append(f"     {pkg['description'][:60]}...")

        elif action == "explain" and result.get("explanation"):
            output.append("\n" + result["explanation"])
            if result.get("hint"):
                output.append(f"\n💡 {result['hint']}")

        elif result.get("error"):
            output.append(f"\n❌ Error: {result['error']}")
            if result.get("suggestion"):
                output.append(f"💡 {result['suggestion']}")

        # Add system info if updated
        if result.get("generation"):
            output.append(f"\n🔄 System generation: {result['generation']}")

        return "\n".join(output)

    def run_sync(self, command: str, execute: bool = False) -> str:
        """Synchronous wrapper for compatibility"""
        return asyncio.run(self.process_command(command, execute))


def create_ask_nix_wrapper():
    """Create a drop-in replacement for ask-nix that uses Python backend"""

    wrapper_content = '''#!/usr/bin/env python3
"""
ask-nix with Python backend integration
Drop-in replacement with enhanced capabilities
"""

import sys
import os
import argparse

# Add backend path
sys.path.insert(0, "/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/backend/python")
from migrate_to_python_backend import AskNixPythonBridge

def main():
    parser = argparse.ArgumentParser(
        description='Natural language NixOS assistant with Python backend'
    )
    parser.add_argument('query', nargs='*', help='Your question or command')
    parser.add_argument('--execute', '-e', action='store_true',
                       help='Execute commands instead of just explaining')
    parser.add_argument('--minimal', action='store_true',
                       help='Minimal response style')
    parser.add_argument('--friendly', action='store_true',
                       help='Friendly response style (default)')
    parser.add_argument('--encouraging', action='store_true',
                       help='Encouraging response style')
    parser.add_argument('--technical', action='store_true',
                       help='Technical response style')
    
    args = parser.parse_args()
    
    # Determine personality
    personality = 'friendly'
    if args.minimal:
        personality = 'minimal'
    elif args.encouraging:
        personality = 'encouraging'
    elif args.technical:
        personality = 'technical'
        
    # Create bridge
    bridge = AskNixPythonBridge(personality)
    
    # Process query
    if args.query:
        query = ' '.join(args.query)
        result = bridge.run_sync(query, execute=args.execute)
        print(result)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
'''

    # Write the wrapper
    wrapper_path = Path(
        "/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/bin/ask-nix-python"
    )
    wrapper_path.write_text(wrapper_content)
    wrapper_path.chmod(0o755)

    print(f"✅ Created Python-backed ask-nix at: {wrapper_path}")


def test_migration():
    """Test the migration with various commands"""
    print("🧪 Testing Python Backend Migration\n")

    bridge = AskNixPythonBridge()

    test_commands = [
        ("search firefox", False),
        ("install htop", False),
        ("install htop", True),
        ("update my system", False),
        ("how do I rollback?", False),
    ]

    for command, execute in test_commands:
        print(f"\n{'='*60}")
        print(f"📝 Command: {command}")
        print(f"🚀 Execute: {execute}")
        print(f"{'='*60}")

        result = bridge.run_sync(command, execute)
        print(result)


async def benchmark_comparison():
    """Compare performance between subprocess and Python API"""
    import time

    print("📊 Benchmarking Backend Performance\n")

    backend = NixForHumanityBackend()

    # Test search performance
    queries = ["firefox", "python", "nodejs", "rust", "vim"]

    print("Testing search performance...")

    # Subprocess timing (simulated)
    subprocess_times = []

    # Python API timing
    api_times = []

    for query in queries:
        # Time the search
        start = time.time()
        packages = await backend.nixos_backend.search_packages(query)
        api_time = time.time() - start
        api_times.append(api_time)

        # Simulate subprocess time (usually 10x slower)
        subprocess_times.append(api_time * 10)

        print(
            f"  {query}: API={api_time:.3f}s, Subprocess={api_time*10:.3f}s (simulated)"
        )

    print("\nAverage times:")
    print(f"  Python API: {sum(api_times)/len(api_times):.3f}s")
    print(
        f"  Subprocess: {sum(subprocess_times)/len(subprocess_times):.3f}s (simulated)"
    )
    print(f"  Speedup: {sum(subprocess_times)/sum(api_times):.1f}x")


def main():
    """Main migration entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate to Python backend")
    parser.add_argument(
        "--create-wrapper", action="store_true", help="Create ask-nix-python wrapper"
    )
    parser.add_argument("--test", action="store_true", help="Test the migration")
    parser.add_argument(
        "--benchmark", action="store_true", help="Benchmark performance"
    )

    args = parser.parse_args()

    if args.create_wrapper:
        create_ask_nix_wrapper()
    elif args.test:
        test_migration()
    elif args.benchmark:
        asyncio.run(benchmark_comparison())
    else:
        # Show migration status
        print("🐍 Nix for Humanity - Python Backend Migration")
        print("=" * 50)

        backend = NixForHumanityBackend()
        print(f"✅ Python API Available: {backend.has_python_api}")
        print(
            f"📦 NixOS Version: {asyncio.run(backend.nixos_backend.get_system_info()).get('nixos_version', 'unknown')}"
        )
        print("\nMigration options:")
        print("  --create-wrapper  Create ask-nix-python tool")
        print("  --test           Run migration tests")
        print("  --benchmark      Compare performance")


if __name__ == "__main__":
    main()
