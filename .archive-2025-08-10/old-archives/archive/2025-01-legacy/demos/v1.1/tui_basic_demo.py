#!/usr/bin/env python3
# Asciinema demo script for tui_basic

import sys
import time


def type_text(text, speed=0.1):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)


def main():
    print("\033[2J\033[H")  # Clear screen
    print("🎬 Nix for Humanity v1.1 - Basic TUI Usage")
    print("=" * 50)
    time.sleep(2)

    time.sleep(2)
    type_text("install firefox", 0.1)
    time.sleep(1)
    print()
    time.sleep(3)
    print("\n✅ Firefox installed successfully")
    time.sleep(2)
    type_text("search markdown", 0.1)
    print()
    time.sleep(2)


if __name__ == "__main__":
    main()
