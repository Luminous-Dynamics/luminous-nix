#!/usr/bin/env python3
"""
Profile startup time to identify bottlenecks
"""

import sys
import time
from pathlib import Path

# Track import times
import_times = {}
original_import = __builtins__.__import__


def timed_import(name, *args, **kwargs):
    start = time.perf_counter()
    module = original_import(name, *args, **kwargs)
    elapsed = time.perf_counter() - start

    if elapsed > 0.01:  # Only track imports taking >10ms
        import_times[name] = import_times.get(name, 0) + elapsed

    return module


# Monkey patch import to track times
__builtins__.__import__ = timed_import

print("Profiling Nix for Humanity startup...")
print("=" * 60)

# Time the overall import
overall_start = time.perf_counter()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import main components
print("\n1. Importing unified backend...")
backend_start = time.perf_counter()

backend_time = time.perf_counter() - backend_start
print(f"   Backend import: {backend_time:.3f}s")

print("\n2. Importing plugins...")
plugin_start = time.perf_counter()

plugin_time = time.perf_counter() - plugin_start
print(f"   Plugin import: {plugin_time:.3f}s")

print("\n3. Importing security...")
security_start = time.perf_counter()

security_time = time.perf_counter() - security_start
print(f"   Security import: {security_time:.3f}s")

overall_time = time.perf_counter() - overall_start

print("\n" + "=" * 60)
print(f"Total import time: {overall_time:.3f}s")
print("\nTop 10 slowest imports:")
print("-" * 40)

# Sort and display slowest imports
sorted_imports = sorted(import_times.items(), key=lambda x: x[1], reverse=True)
for name, elapsed in sorted_imports[:10]:
    print(f"{elapsed:.3f}s - {name}")

print("\n" + "=" * 60)
print("Analysis:")
print("-" * 40)

# Identify biggest bottlenecks
total_tracked = sum(import_times.values())
print(f"Time in tracked imports: {total_tracked:.3f}s")
print(f"Other overhead: {overall_time - total_tracked:.3f}s")

# Specific problem areas
if backend_time > 0.5:
    print(f"\n⚠️  Backend import is slow ({backend_time:.3f}s)")
    print("   Consider lazy loading heavy dependencies")

if any("nix" in name for name in import_times):
    nix_time = sum(t for n, t in import_times.items() if "nix" in n)
    print(f"\n⚠️  Nix-related imports: {nix_time:.3f}s")
    print("   Consider deferring nixos-rebuild module loading")

# Recommendations
print("\n" + "=" * 60)
print("Recommendations:")
print("-" * 40)

if overall_time > 1.0:
    print("1. Implement lazy imports for heavy modules")
    print("2. Use __init__.py to control what's imported")
    print("3. Defer expensive initialization until needed")
    print("4. Consider caching initialized modules")

print("\nNext step: Create optimized version with lazy loading")
