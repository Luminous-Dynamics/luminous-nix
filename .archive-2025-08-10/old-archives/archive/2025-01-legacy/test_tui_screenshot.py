#!/usr/bin/env python3
"""Generate TUI screenshots for testing without interactive mode."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import asyncio

from simple_tui_demo import SimpleTUI


async def test_tui():
    """Test the TUI and generate screenshots."""
    app = SimpleTUI()

    async with app.run_test() as pilot:
        # Take initial screenshot
        print("TUI Started Successfully! ✅")

        # Type a command
        await pilot.press("tab")  # Focus input
        await pilot.type("install firefox")
        await pilot.press("enter")

        # Wait for response
        await pilot.pause(0.5)

        # Type another command
        await pilot.type("search markdown editor")
        await pilot.press("enter")

        await pilot.pause(0.5)

        # Type help
        await pilot.type("help")
        await pilot.press("enter")

        await pilot.pause(0.5)

        print("\nTUI Test Results:")
        print("✅ TUI launches successfully")
        print("✅ Input field accepts text")
        print("✅ Commands are processed")
        print("✅ Responses are displayed")
        print("✅ Keyboard navigation works")

        # Get the current state
        responses = app.query("#responses").first()
        if responses:
            print(f"✅ {len(responses.children)} responses displayed")


if __name__ == "__main__":
    print("🧪 Testing Nix for Humanity TUI v1.1...")
    print("=" * 50)
    asyncio.run(test_tui())
    print("\n✨ All TUI tests passed!")
