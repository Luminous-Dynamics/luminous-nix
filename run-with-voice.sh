#!/usr/bin/env bash
# Run Nix for Humanity with proper voice library paths

echo "🎤 Setting up voice environment..."

# Find and export library paths
export LD_LIBRARY_PATH="/run/current-system/sw/lib:$LD_LIBRARY_PATH"

# Find GCC libraries
GCC_LIB=$(find /nix/store -name "libstdc++.so.6" -type f 2>/dev/null | head -1 | xargs dirname)
if [ -n "$GCC_LIB" ]; then
    export LD_LIBRARY_PATH="$GCC_LIB:$LD_LIBRARY_PATH"
    echo "✅ Found libstdc++ at $GCC_LIB"
fi

# Find PortAudio
PORTAUDIO_LIB=$(find /nix/store -name "libportaudio.so" -type f 2>/dev/null | head -1 | xargs dirname)
if [ -n "$PORTAUDIO_LIB" ]; then
    export LD_LIBRARY_PATH="$PORTAUDIO_LIB:$LD_LIBRARY_PATH"
    echo "✅ Found PortAudio at $PORTAUDIO_LIB"
fi

echo "Library path set: $LD_LIBRARY_PATH"
echo

# Run the command passed as arguments, or start TUI if no args
if [ $# -eq 0 ]; then
    echo "Starting TUI with voice support..."
    poetry run python -m nix_for_humanity.tui.app
else
    poetry run "$@"
fi