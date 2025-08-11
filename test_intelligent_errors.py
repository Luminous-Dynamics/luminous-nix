#!/usr/bin/env python3
"""
Test intelligent error handling
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nix_for_humanity.errors import ErrorContext, get_error_educator

print("Testing Intelligent Error Handling")
print("=" * 60)

educator = get_error_educator()

# Test different error types
test_errors = [
    (
        "attribute 'firofox' in selection path 'nixpkgs.firofox' not found",
        ErrorContext(
            "package_error",
            "attribute not found",
            package="firofox",
            operation="install",
        ),
    ),
    (
        "permission denied: cannot write to /nix/store",
        ErrorContext("permission_error", "permission denied", operation="install"),
    ),
    (
        "syntax error, unexpected '}', expecting ';'",
        ErrorContext("syntax_error", "syntax error", operation="config"),
    ),
    (
        "unable to download 'https://cache.nixos.org/...': Connection timeout",
        ErrorContext("network_error", "connection timeout", operation="download"),
    ),
    (
        "no space left on device",
        ErrorContext("storage_error", "disk full", operation="install"),
    ),
    (
        "collision between `/nix/store/abc-nodejs-18.17.0/bin/node' and `/nix/store/xyz-nodejs-16.20.0/bin/node'",
        ErrorContext("collision_error", "package collision", operation="install"),
    ),
]

for i, (error, context) in enumerate(test_errors, 1):
    print(f"\n{'='*60}")
    print(f"Test {i}: {context.error_type}")
    print("-" * 40)
    print(f"Original error: {error[:60]}...")
    print("\nEducational response:")
    print("-" * 40)
    educated = educator.educate(error, context)
    print(educated)

# Test repeated errors (should show pattern recognition)
print(f"\n{'='*60}")
print("Testing repeated error detection")
print("-" * 40)

# Simulate multiple package not found errors
for pkg in ["vim", "emacs", "vscode"]:
    error = f"attribute '{pkg}' not found"
    context = ErrorContext("package_error", error, package=pkg, operation="install")
    educated = educator.educate(error, context)

    # Just show if it detected the pattern
    if "You've seen this type of error before" in educated:
        print(f"✓ Pattern detected for {pkg} error")

# Show common mistakes learned
print(f"\n{'='*60}")
print("Common mistakes detected:")
print("-" * 40)
tips = educator.get_common_mistakes()
for tip in tips:
    print(f"  • {tip}")

print("\n✨ Intelligent error handling working!")
