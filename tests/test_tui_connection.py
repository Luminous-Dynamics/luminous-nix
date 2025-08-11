#!/usr/bin/env python3
import sys

sys.path.insert(0, "src")

from nix_for_humanity.api.schema import Request
from nix_for_humanity.core.engine import NixForHumanityBackend

try:
    backend = NixForHumanityBackend()
    request = Request(query="help")

    # Test sync wrapper
    response = backend.process(request)
    print(f"✅ Sync wrapper works: {response.success}")

    # Test if backend has all TUI methods
    methods = [
        "get_current_context",
        "get_settings",
        "execute_command",
        "get_suggestions",
    ]
    for method in methods:
        if hasattr(backend, method):
            print(f"✅ {method} available")
        else:
            print(f"❌ {method} missing")

except Exception as e:
    print(f"❌ Test failed: {e}")
