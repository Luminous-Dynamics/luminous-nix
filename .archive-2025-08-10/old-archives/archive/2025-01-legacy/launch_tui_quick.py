#!/usr/bin/env python3
"""Quick TUI launcher with minimal dependencies."""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))


# Create a minimal mock backend for testing
class MockBackend:
    def process_query(self, query):
        """Process a query and return a response."""
        responses = {
            "install firefox": {
                "confidence": 0.95,
                "command": "nix-env -iA nixos.firefox",
                "explanation": "This will install Firefox using nix-env",
                "alternatives": [
                    {
                        "command": "nix profile install nixpkgs#firefox",
                        "description": "Using new nix profile",
                    }
                ],
            },
            "search markdown": {
                "confidence": 0.90,
                "command": "nix search nixpkgs markdown",
                "explanation": "Search for markdown-related packages",
                "results": [
                    {"name": "obsidian", "description": "Powerful knowledge base"},
                    {"name": "marktext", "description": "Simple markdown editor"},
                ],
            },
        }

        # Default response
        default = {
            "confidence": 0.70,
            "command": f"# Query: {query}",
            "explanation": "I'm understanding your request...",
            "suggestions": ["Try 'install [package]' or 'search [term]'"],
        }

        # Simple matching
        for key, response in responses.items():
            if key in query.lower():
                return response

        return default


# NOTE: Animation issue fixed directly in consciousness_orb.py

# Import and run the TUI
try:
    from nix_humanity.ui.main_app import NixForHumanityTUI

    # Create app with mock backend
    app = NixForHumanityTUI()
    app.backend = MockBackend()

    # Run the app
    app.run()
except ImportError as e:
    print(f"Error importing TUI: {e}")
    print("\nDetailed error:")
    import traceback

    traceback.print_exc()

    # Check if we're missing dependencies
    print("\nChecking dependencies...")
    try:
        import textual

        print("✓ Textual is installed")
    except ImportError:
        print("✗ Textual is NOT installed")

    try:
        import rich

        print("✓ Rich is installed")
    except ImportError:
        print("✗ Rich is NOT installed")
except Exception as e:
    print(f"Error running TUI: {e}")
    import traceback

    traceback.print_exc()
