#!/usr/bin/env python3
"""
Demo: Adaptive Response System in Action

Shows how the same question gets different responses based on
detected user state and natural language cues.
"""

import importlib.util
import os
import sys

# Add parent directory to path
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(script_dir)

# Import adaptive response formatter using importlib
spec = importlib.util.spec_from_file_location(
    "adaptive_response_formatter",
    os.path.join(script_dir, "adaptive-response-formatter.py"),
)
adaptive_response_formatter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adaptive_response_formatter)
AdaptiveResponseFormatter = adaptive_response_formatter.AdaptiveResponseFormatter


def demo_adaptive_responses():
    """Demonstrate the adaptive response system"""
    formatter = AdaptiveResponseFormatter()

    # Base response about installing Firefox
    base_response = """I'll help you install Firefox! Here are your options:

1. **Home Manager** (User-level) - No sudo needed
   Edit ~/.config/home-manager/home.nix and add:
   ```
   home.packages = with pkgs; [ firefox ];
   ```
   Then run: home-manager switch

2. **Nix Profile** (Quick install) - Modern approach
   ```
   nix profile install nixpkgs#firefox
   ```

3. **System-wide** (Permanent) - Requires sudo
   Edit /etc/nixos/configuration.nix and add to environment.systemPackages:
   ```
   environment.systemPackages = with pkgs; [ firefox ];
   ```
   Then run: sudo nixos-rebuild switch

💡 The nix profile method is quickest for trying out new software."""

    # Different user queries showing various states
    test_cases = [
        {
            "name": "Beginner User",
            "query": "How do I install Firefox? I'm new to NixOS and confused.",
            "expected": "Simple language, warm tone, fewer options",
        },
        {
            "name": "Time-Pressured User",
            "query": "quickly tell me how to install firefox",
            "expected": "Ultra-concise, just the command",
        },
        {
            "name": "Learning User",
            "query": "Can you explain step by step how to install Firefox and why?",
            "expected": "Detailed, educational, with examples",
        },
        {
            "name": "Frustrated User",
            "query": "Firefox install not working, this is so frustrating!",
            "expected": "Reassuring, simple steps, high warmth",
        },
        {
            "name": "Accessibility User",
            "query": "My screen reader needs simple instructions for installing Firefox",
            "expected": "Plain text, no formatting, very concise",
        },
        {
            "name": "Technical User",
            "query": "Give me the exact technical details for Firefox installation methods",
            "expected": "Full technical detail, all options",
        },
        {
            "name": "Mobile User",
            "query": "install firefox mobile quick",
            "expected": "Minimal verbosity, direct answer",
        },
    ]

    print("🎯 Adaptive Response System Demonstration")
    print("=" * 80)
    print("\nShowing how the same base response adapts to different user needs:\n")

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}: {test['name']}")
        print(f"Query: \"{test['query']}\"")
        print(f"Expected: {test['expected']}")
        print("-" * 80)

        # Get adapted response
        adapted, dimensions = formatter.adapt_response(
            test["query"], base_response, "install_package"
        )

        print("Response:")
        print(adapted)

        print("\nDimensions:")
        print(
            f"  Complexity: {dimensions.complexity:.1f} "
            f"({'simple' if dimensions.complexity < 0.5 else 'technical'})"
        )
        print(
            f"  Verbosity: {dimensions.verbosity:.1f} "
            f"({'concise' if dimensions.verbosity < 0.5 else 'detailed'})"
        )
        print(
            f"  Warmth: {dimensions.warmth:.1f} "
            f"({'neutral' if dimensions.warmth < 0.5 else 'friendly'})"
        )
        print(
            f"  Examples: {dimensions.examples:.1f} "
            f"({'minimal' if dimensions.examples < 0.5 else 'many'})"
        )
        print(
            f"  Visual: {dimensions.visual_structure:.1f} "
            f"({'plain' if dimensions.visual_structure < 0.3 else 'formatted'})"
        )

    print("\n" + "=" * 80)
    print("\n✨ Key Insights:")
    print("- Same base content, dramatically different presentations")
    print("- Responds to emotional state (frustration, confusion)")
    print("- Adapts to time pressure and urgency")
    print("- Respects accessibility needs automatically")
    print("- No need to manually select personality modes")
    print("\n🎯 This is consciousness-first computing in action!")


if __name__ == "__main__":
    demo_adaptive_responses()
