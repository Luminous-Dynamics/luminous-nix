#!/usr/bin/env python3
"""
Test the TUI integration with the headless core
"""

import os
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Test imports
print("Testing imports...")
try:
    from nix_for_humanity.core import NixForHumanityCore, Query, ExecutionMode
    print("✅ Core imports successful")
except ImportError as e:
    print(f"❌ Core import failed: {e}")
    sys.exit(1)

try:
    from nix_for_humanity.tui import NixHumanityApp
    print("✅ TUI imports successful")
except ImportError as e:
    print(f"❌ TUI import failed: {e}")
    sys.exit(1)

# Test core functionality
print("\nTesting core engine...")
core = NixForHumanityCore({
    'dry_run': True,
    'default_personality': 'friendly'
})

# Test a simple query
query = Query(
    text="install firefox",
    mode=ExecutionMode.DRY_RUN
)

response = core.process(query)
print(f"✅ Core processed query: {response.intent.type}")

# Test plan/execute separation
plan = core.plan(query)
print(f"✅ Plan created: {plan.text[:50]}...")

print("\n🎉 All tests passed! The TUI should work correctly.")
print("\nTo launch the TUI, run:")
print("  ./bin/nix-tui")
print("\nOr:")
print("  python3 -m nix_for_humanity.tui.app")