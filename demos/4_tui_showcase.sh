#!/bin/bash
# Demo script for Luminous Nix
# Convert to GIF with: asciinema rec -c ./demo.sh demo.cast
# Then: docker run --rm -v $PWD:/data asciinema/asciicast2gif demo.cast demo.gif

clear
echo "🌟 Luminous Nix Demo"
sleep 1

echo -n "$ "
sleep 0.5
echo -n "n"
sleep 0.05
echo -n "i"
sleep 0.05
echo -n "x"
sleep 0.05
echo -n "-"
sleep 0.05
echo -n "t"
sleep 0.05
echo -n "u"
sleep 0.05
echo -n "i"
sleep 0.05
echo ""
sleep 0.5
nix-tui
sleep 5

echo ""
echo "✨ Demo complete!"
sleep 2
