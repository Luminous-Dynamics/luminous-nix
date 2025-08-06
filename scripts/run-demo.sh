#!/bin/bash

echo "🧹 Cleaning up..."
pkill -f vite 2>/dev/null
rm -rf node_modules/.vite 2>/dev/null

echo "🚀 Starting Nix for Humanity Demo..."
echo ""
echo "The demo will start at: http://localhost:5173/demo"
echo ""
echo "If port 5173 is busy, it will use the next available port."
echo "Watch for the URL in the output below."
echo ""

# Start vite in the background
npm run demo &

# Give it a moment to start
sleep 3

echo ""
echo "📝 Instructions:"
echo "1. Open your browser to the URL shown above"
echo "2. Try the privacy transparency features"
echo "3. Test different personality styles" 
echo "4. Explore the persona testing mode"
echo ""
echo "Press Ctrl+C to stop the demo server"

# Keep the script running
wait