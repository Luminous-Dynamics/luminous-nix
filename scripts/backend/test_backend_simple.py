#!/usr/bin/env python3
"""Simple test of the Python backend"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from nix_python_backend import NixPythonBackend

print("🐍 Testing Nix Python Backend")
print("=" * 40)

# Create backend
backend = NixPythonBackend()

print("✅ Backend created")
print(f"📊 API Available: {backend.api_available}")

# Test simple operations
print("\n🔍 Testing package search:")
packages = backend.search_packages("python")
print(f"Found {len(packages)} packages")
for pkg in packages[:3]:
    print(f"  - {pkg['name']} ({pkg['version']})")

print("\n📋 Testing list generations:")
result = backend.list_generations()
if result.success:
    gens = result.details.get("generations", [])
    print(f"Found {len(gens)} generations")
    if gens:
        latest = gens[-1]
        print(f"Latest: Generation {latest['number']} ({latest['date']})")

print("\n✅ Backend test complete!")
