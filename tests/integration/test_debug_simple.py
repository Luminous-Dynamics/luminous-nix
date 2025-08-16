#!/usr/bin/env python3
"""
Debug test to identify the timeout issue
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

print("Starting debug test...")

try:
    print("Importing Query and str...")
except Exception as e:
    print(f"Error during initial setup: {e}")
    
# Mock Query if not available
try:
    from luminous_nix.api.schema import Request as Query
except (ImportError, AttributeError):
    class Query:
        def __init__(self, text="", context=None, **kwargs):
            self.text = text
            self.context = context or {}
            for k, v in kwargs.items():
                setattr(self, k, v)


    print("✓ Imports successful")

    print("\nCreating Query object...")
    query = {"query": "install vim", "mode": "dry_run"}
    print(f"✓ Query created: {query}")

    print("\nImporting Engine...")
    from luminous_nix.core.engine import NixForHumanityBackend as Engine

    print("✓ Engine imported")

    print("\nCreating Engine instance...")
    config = {"dry_run": True, "default_personality": "friendly"}
    engine = Engine(config)
    print("✓ Engine created")

    print("\nProcessing query...")
    response = engine.process(query)
    print(f"✓ Response: {response}")
    print(f"Response text: {response.text}")

except Exception as e:
    print(f"\n✗ Error: {type(e).__name__}: {e}")
    import traceback

    traceback.print_exc()

print("\nDebug test complete.")
