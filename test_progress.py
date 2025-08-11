#!/usr/bin/env python3
"""
Test progress indicators
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nix_for_humanity.ui.progress import PhaseProgress, ProgressBar, Spinner

print("Testing Progress Indicators")
print("=" * 60)

# Test 1: Spinner
print("\n1. Testing Spinner")
with Spinner("Loading packages"):
    time.sleep(2)

# Test 2: Progress Bar
print("\n2. Testing Progress Bar")
bar = ProgressBar(10, "Installing packages")
for i in range(10):
    time.sleep(0.2)
    bar.update()

# Test 3: Phase Progress
print("\n3. Testing Phase Progress")
phases = [
    "Evaluating configuration",
    "Building derivations",
    "Downloading packages",
    "Activating configuration",
    "Setting up services",
]

progress = PhaseProgress(phases)
for i in range(len(phases)):
    progress.start_phase(i)
    time.sleep(1)
progress.complete("System update complete!")

print("\n✨ All progress indicators working!")
