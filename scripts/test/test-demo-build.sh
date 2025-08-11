#!/bin/bash

echo "🏗️ Building demo..."
npm run build

echo ""
echo "📁 Build output:"
ls -la dist/

echo ""
echo "🌐 To view the demo:"
echo "1. Open a simple HTTP server in the dist directory:"
echo "   cd dist && python3 -m http.server 8000"
echo ""
echo "2. Open your browser to:"
echo "   http://localhost:8000/demo.html"
echo ""
echo "✨ Demo build complete!"
