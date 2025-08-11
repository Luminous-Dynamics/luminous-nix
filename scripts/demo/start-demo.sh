#!/bin/bash
# 🚀 Nix for Humanity Demo Launcher
# Quick setup and launch script for the integrated demo

echo "🌟 Nix for Humanity Demo Launcher"
echo "================================="
echo

# Check for Node.js
if ! command -v npm &> /dev/null; then
    echo "❌ Error: Node.js is not installed."
    echo "Please install Node.js 18+ first:"
    echo "  - NixOS: nix-shell -p nodejs_20"
    echo "  - Ubuntu/Debian: sudo apt install nodejs npm"
    echo "  - macOS: brew install node"
    exit 1
fi

# Check Node version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Error: Node.js 18+ required (found v$NODE_VERSION)"
    exit 1
fi

echo "✅ Node.js $(node -v) detected"
echo

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

echo

# Check if vite is available
if [ ! -f "node_modules/.bin/vite" ]; then
    echo "📦 Installing Vite..."
    npm install --save-dev vite @vitejs/plugin-react
fi

# Create vite config if missing
if [ ! -f "vite.config.ts" ]; then
    echo "📝 Creating Vite configuration..."
    cat > vite.config.ts << 'EOF'
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    open: '/demo',
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});
EOF
fi

# Create index.html if missing
if [ ! -f "index.html" ]; then
    echo "📝 Creating index.html..."
    cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Nix for Humanity - Demo</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF
fi

# Create main.tsx if missing
if [ ! -f "src/main.tsx" ]; then
    echo "📝 Creating main entry point..."
    mkdir -p src
    cat > src/main.tsx << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import { IntegratedSystemDemo } from './demo/IntegratedSystemDemo';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <IntegratedSystemDemo />
  </React.StrictMode>
);
EOF
fi

# Create basic CSS if missing
if [ ! -f "src/index.css" ]; then
    echo "📝 Creating styles..."
    cat > src/index.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
EOF
fi

# Update package.json scripts
echo "📝 Updating package.json scripts..."
node -e "
const pkg = require('./package.json');
pkg.scripts = pkg.scripts || {};
pkg.scripts['demo'] = 'vite';
pkg.scripts['demo:build'] = 'vite build';
pkg.scripts['demo:preview'] = 'vite preview';
require('fs').writeFileSync('./package.json', JSON.stringify(pkg, null, 2));
"

echo
echo "🎯 Starting Nix for Humanity Demo..."
echo "===================================="
echo
echo "The demo will open automatically at http://localhost:5173/demo"
echo "Press Ctrl+C to stop the demo server"
echo

# Start the demo
npm run demo
