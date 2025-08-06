#!/usr/bin/env bash
# Monitor script to check when Python becomes available

echo "🔍 Monitoring Python availability..."
echo "Press Ctrl+C to stop"
echo

while true; do
    if command -v python3 &> /dev/null; then
        echo "✅ Python 3 is now available!"
        python3 --version
        echo
        echo "You can now run:"
        echo "  cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity"
        echo "  ./test-phase-0.sh"
        echo
        echo "Or test directly:"
        echo "  ./bin/ask-nix-hybrid-v2 --execute 'install firefox'"
        
        # Play a sound if available
        if command -v paplay &> /dev/null && [ -f /usr/share/sounds/freedesktop/stereo/complete.oga ]; then
            paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null
        elif command -v beep &> /dev/null; then
            beep 2>/dev/null
        fi
        
        break
    else
        echo -n "."
        sleep 5
    fi
done