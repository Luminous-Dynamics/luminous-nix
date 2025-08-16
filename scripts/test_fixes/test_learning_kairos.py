#!/usr/bin/env python3
"""
Test the pragmatic learning with kairos improvements.
Kairos = perfect timing - learn at the right pace.
"""

import sys

sys.path.insert(0, "src")

from luminous_nix.learning.pragmatic_learning import PragmaticLearningSystem

# Create test user with adaptive thresholds
learning = PragmaticLearningSystem("kairos_test")

# Kairos improvement: Lower thresholds for new users
total_commands = sum(learning.preferences.command_frequency.values())
if total_commands < 10:
    learning.ALIAS_THRESHOLD = 2  # Learn faster when new
    learning.SEQUENCE_THRESHOLD = 2
    print("🌱 New user detected - learning eagerly")
else:
    print("🌳 Experienced user - learning conservatively")

print("\n📚 Simulating realistic usage...")
print("-" * 40)

# More realistic command sequence
commands = [
    # User tries their own vocabulary
    ("grab firefox", False, "unknown command: grab"),
    ("install firefox", True, None),
    # They try again with muscle memory
    ("grab vscode", False, "unknown command: grab"),
    ("install vscode", True, None),
    # Third time - should learn now with kairos threshold
    ("grab neovim", False, "unknown command: grab"),
    ("install neovim", True, None),
    # Common workflow pattern
    ("nixos-rebuild switch", True, None),
    ("nix-collect-garbage", True, None),
    # Repeat the workflow
    ("nixos-rebuild switch", True, None),
    ("nix-collect-garbage", True, None),
]

for i, (cmd, success, error) in enumerate(commands, 1):
    print(f"\n[{i}] User: {cmd}")

    # Check for suggestions BEFORE the command
    alias_suggestion = learning.suggest_alias(cmd)
    if alias_suggestion:
        print(f"    💡 {alias_suggestion}")

    # Execute and learn
    learning.observe_command(cmd, success, error)

    # Show feedback
    if not success:
        print(f"    ❌ {error}")
        error_fix = learning.suggest_error_fix(error)
        if error_fix:
            print(f"    💡 {error_fix}")
    else:
        print("    ✅ Success")

        # Suggest next command
        next_suggestion = learning.suggest_next_command(cmd)
        if next_suggestion:
            print(f"    🔮 {next_suggestion}")

# Show what was learned
print("\n" + "=" * 50)
print("🧠 Learning Summary")
print("=" * 50)
print(learning.export_learnings())

# Test the learned patterns
print("\n" + "=" * 50)
print("🎯 Testing Learned Patterns")
print("=" * 50)

test_commands = [
    "grab docker",  # Should suggest install
    "nixos-rebuild switch",  # Should suggest garbage collection
]

for cmd in test_commands:
    print(f"\nUser types: {cmd}")

    alias = learning.suggest_alias(cmd)
    if alias:
        print(f"  💡 {alias}")

    next_cmd = learning.suggest_next_command(cmd)
    if next_cmd:
        print(f"  🔮 {next_cmd}")

# Kairos insight
print("\n" + "=" * 50)
print("✨ Kairos Insights")
print("=" * 50)
verbosity = learning.get_verbosity_preference()
active_hours = learning.get_active_hours_summary()

print(f"Verbosity preference: {verbosity}")
print(f"Active pattern: {active_hours}")
print("\n🌊 The system learns at the perfect pace,")
print("   eager when you're new, patient when you're experienced.")
