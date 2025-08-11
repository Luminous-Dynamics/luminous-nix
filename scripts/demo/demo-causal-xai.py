#!/usr/bin/env python3
"""
Demo of Causal XAI features in Nix for Humanity
"""

import subprocess
import sys

print("🧠 Causal XAI Demo for Nix for Humanity")
print("=" * 50)

demos = [
    {
        "title": "Simple Why Explanation",
        "command": ["ask-nix-xai", "--why", "install firefox"],
        "description": "Get a quick explanation of why a command is suggested",
    },
    {
        "title": "Detailed Causal Explanation",
        "command": ["ask-nix-xai", "--explain", "update my system"],
        "description": "See detailed reasoning with confidence scores",
    },
    {
        "title": "Technical Explanation",
        "command": [
            "ask-nix-xai",
            "--explain",
            "--technical",
            "remove unused packages",
        ],
        "description": "Get technical details including causal graphs",
    },
    {
        "title": "Error Explanation",
        "command": ["ask-nix-xai", "--dry-run", "install nonexistent-package"],
        "description": "Understand why errors occur and how to fix them",
    },
]

for demo in demos:
    print(f"\n📋 {demo['title']}")
    print(f"   {demo['description']}")
    print(f"\n   Command: {' '.join(demo['command'])}")
    print("   " + "-" * 40)

    try:
        # Run the command
        result = subprocess.run(
            demo["command"], capture_output=True, text=True, timeout=10
        )

        # Show output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"   ⚠️ Error: {result.stderr}", file=sys.stderr)

    except subprocess.TimeoutExpired:
        print("   ⏱️ Command timed out")
    except Exception as e:
        print(f"   ❌ Error running demo: {e}")

    input("\nPress Enter to continue...")

print("\n✅ Demo complete!")
print("\nTo use XAI in your daily workflow:")
print("  • Add --why for quick explanations")
print("  • Add --explain for detailed reasoning")
print("  • The AI will explain its confidence and reasoning")
