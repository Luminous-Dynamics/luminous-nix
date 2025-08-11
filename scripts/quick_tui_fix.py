#!/usr/bin/env python3
"""Quick fix to run TUI without the consciousness orb animation issue."""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Monkey patch the animate_breathing method
from nix_for_humanity.ui.consciousness_orb import ConsciousnessOrb


def fixed_animate_breathing(self):
    """Fixed breathing animation - just sets the value directly"""
    self.pulse_intensity = 0.3 if self.ai_state.value == "idle" else 0.8
    self.refresh()


# Replace the method
ConsciousnessOrb.animate_breathing = fixed_animate_breathing

# Now run the app
from nix_for_humanity.ui.main_app import NixForHumanityTUI

if __name__ == "__main__":
    app = NixForHumanityTUI()
    app.run()
