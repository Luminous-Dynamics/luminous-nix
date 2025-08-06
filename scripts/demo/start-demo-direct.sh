#!/bin/bash

# Start in current directory
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity

# Kill any existing vite process
pkill -f vite 2>/dev/null

echo "Starting demo server..."
echo "Please wait for the server to start..."
echo ""

# Start vite directly with explicit config
npx vite --port 5173 --open /demo &

# Wait a moment
sleep 5

echo ""
echo "Demo should be available at:"
echo "  http://localhost:5173/demo"
echo ""
echo "If you see errors above, try:"
echo "  1. npm install"
echo "  2. Then run this script again"
echo ""
echo "Press Ctrl+C to stop"

# Keep script running
wait