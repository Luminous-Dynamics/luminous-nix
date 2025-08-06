#!/usr/bin/env bash
# Quick development setup

echo "📦 Installing dependencies..."
npm install

echo "🔨 Building all packages..."
npm run build

echo "✅ Ready for development!"
echo ""
echo "Available commands:"
echo "  npm run build    - Build all packages"
echo "  npm run test     - Run all tests"
echo "  npm run lint     - Lint all code"
echo "  npm run check    - Type check all code"
echo ""
echo "Start developing in packages/*"
