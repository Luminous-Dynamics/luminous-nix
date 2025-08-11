#!/usr/bin/env python3
"""
Test optimized startup time
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("Testing optimized startup time...")
print("=" * 60)

# Test 1: Minimal import
print("\n1. Minimal import (just backend class)")
start = time.perf_counter()
from nix_for_humanity.core.unified_backend import NixForHumanityBackend

elapsed1 = time.perf_counter() - start
print(f"   Import time: {elapsed1:.3f}s")

# Test 2: Create backend instance (should be fast with lazy loading)
print("\n2. Create backend instance (lazy)")
start = time.perf_counter()
backend = NixForHumanityBackend()
elapsed2 = time.perf_counter() - start
print(f"   Creation time: {elapsed2:.3f}s")

# Test 3: First actual use (will trigger lazy loads)
print("\n3. First command (triggers lazy load)")
start = time.perf_counter()
import asyncio

result = asyncio.run(backend.execute("help"))
elapsed3 = time.perf_counter() - start
print(f"   First command: {elapsed3:.3f}s")

# Test 4: Second command (should be faster, already loaded)
print("\n4. Second command (already loaded)")
start = time.perf_counter()
result = asyncio.run(backend.execute("test"))
elapsed4 = time.perf_counter() - start
print(f"   Second command: {elapsed4:.3f}s")

# Summary
print("\n" + "=" * 60)
print("Performance Summary:")
print("-" * 40)
total_first = elapsed1 + elapsed2 + elapsed3
print(f"Total first command: {total_first:.3f}s")
print(f"Subsequent commands: {elapsed4:.3f}s")

if total_first < 1.0:
    print("\n✅ SUCCESS: Startup under 1 second!")
else:
    print(f"\n⚠️  Still needs optimization: {total_first:.3f}s > 1.0s target")

# Breakdown
print("\nBreakdown:")
print(f"  Import overhead: {elapsed1:.3f}s ({elapsed1/total_first*100:.1f}%)")
print(f"  Backend creation: {elapsed2:.3f}s ({elapsed2/total_first*100:.1f}%)")
print(f"  First execution: {elapsed3:.3f}s ({elapsed3/total_first*100:.1f}%)")
