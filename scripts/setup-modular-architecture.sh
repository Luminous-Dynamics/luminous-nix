#!/usr/bin/env bash
# setup-modular-architecture.sh
# Creates the modular package structure for Nix for Humanity

set -e  # Exit on error

echo "🏗️  Setting up modular architecture for Nix for Humanity"
echo "=================================================="

# Base directory
BASE_DIR="$(dirname "$0")"
cd "$BASE_DIR"

# Create package directories
echo "📁 Creating package structure..."
mkdir -p packages/{core,nlp,executor,patterns,personality,learning,ui}/{src,test}

# Create base TypeScript config
echo "📝 Creating base TypeScript configuration..."
cat > tsconfig.base.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "lib": ["ES2022"],
    "moduleResolution": "node",
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
EOF

# Create root package.json
echo "📦 Creating root package.json..."
cat > package.json << 'EOF'
{
  "name": "nix-for-humanity",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "workspaces": [
    "packages/*"
  ],
  "scripts": {
    "build": "npm run build --workspaces",
    "test": "npm run test --workspaces",
    "lint": "eslint packages/*/src/**/*.ts",
    "check": "tsc --noEmit",
    "clean": "rm -rf packages/*/dist packages/*/node_modules node_modules"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "prettier": "^3.0.0"
  },
  "engines": {
    "node": ">=20.0.0"
  }
}
EOF

# Package-specific configurations
declare -A PACKAGE_DESCRIPTIONS=(
  ["core"]="Shared types, constants, and utilities"
  ["nlp"]="Natural Language Processing engine"
  ["executor"]="Safe command execution engine"
  ["patterns"]="Single source of truth for all patterns"
  ["personality"]="Adaptive personality system (5 styles)"
  ["learning"]="User preference learning system"
  ["ui"]="User interfaces (CLI, future Tauri)"
)

# Create individual packages
for pkg in core nlp executor patterns personality learning ui; do
  echo "📦 Setting up @nix-humanity/$pkg..."
  
  # Package.json
  cat > packages/$pkg/package.json << EOF
{
  "name": "@nix-humanity/$pkg",
  "version": "0.1.0",
  "description": "${PACKAGE_DESCRIPTIONS[$pkg]}",
  "type": "module",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "files": ["dist"],
  "scripts": {
    "build": "tsc",
    "test": "node --test test/**/*.test.js",
    "clean": "rm -rf dist"
  },
  "dependencies": {},
  "devDependencies": {}
}
EOF

  # TypeScript config
  cat > packages/$pkg/tsconfig.json << EOF
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "test"]
}
EOF

  # Create index.ts with basic exports
  case $pkg in
    "core")
      cat > packages/$pkg/src/index.ts << 'EOF'
// @nix-humanity/core - Shared types, constants, and utilities

export interface Intent {
  action: string;
  target?: string;
  modifiers?: Record<string, any>;
  confidence: number;
}

export interface CommandResult {
  success: boolean;
  output?: string;
  error?: Error;
  suggestions?: string[];
}

export interface PersonalityStyle {
  name: 'minimal' | 'friendly' | 'encouraging' | 'playful' | 'sacred';
  formality: number;
  verbosity: number;
  emotionality: number;
  encouragement: number;
  playfulness: number;
  spirituality: number;
}

export interface UserPreferences {
  personalityStyle: PersonalityStyle['name'];
  commandHistory: string[];
  aliases: Record<string, string>;
}

// Re-export everything
export * from './types';
export * from './constants';
export * from './utils';
EOF
      ;;
    
    "nlp")
      cat > packages/$pkg/src/index.ts << 'EOF'
// @nix-humanity/nlp - Natural Language Processing engine

import type { Intent } from '@nix-humanity/core';

export class NLPEngine {
  async parse(input: string): Promise<Intent> {
    // TODO: Consolidate existing implementations
    throw new Error('Not implemented yet');
  }
}

export { FuzzyMatcher } from './fuzzy-matcher';
export { ContextTracker } from './context-tracker';
export { ErrorRecovery } from './error-recovery';
EOF
      ;;
    
    "executor")
      cat > packages/$pkg/src/index.ts << 'EOF'
// @nix-humanity/executor - Safe command execution engine

import type { CommandResult } from '@nix-humanity/core';

export class CommandExecutor {
  async execute(command: string, args: string[]): Promise<CommandResult> {
    // TODO: Implement safe execution
    throw new Error('Not implemented yet');
  }
}

export { Validator } from './validator';
export { Sandbox } from './sandbox';
export { PermissionChecker } from './permissions';
EOF
      ;;
    
    "patterns")
      cat > packages/$pkg/src/index.ts << 'EOF'
// @nix-humanity/patterns - Single source of truth for all patterns

export const PATTERNS = {
  install: {
    patterns: [
      /^(install|add|get)\s+(.+)$/i,
      /^i\s+(need|want)\s+(.+)$/i,
      /^(can you |please |could you )?install\s+(.+?)(\s+for me)?$/i,
    ],
    examples: [
      'install firefox',
      'add nodejs', 
      'get me chrome',
      'i need python',
      'please install vscode for me'
    ],
    nixCommand: 'nix-env -iA nixos.{package}'
  },
  
  remove: {
    patterns: [
      /^(remove|uninstall|delete)\s+(.+)$/i,
      /^get rid of\s+(.+)$/i,
    ],
    examples: [
      'remove firefox',
      'uninstall chrome',
      'get rid of old python'
    ],
    nixCommand: 'nix-env -e {package}'
  },
  
  update: {
    patterns: [
      /^update(\s+system)?$/i,
      /^upgrade(\s+everything)?$/i,
    ],
    examples: [
      'update',
      'update system',
      'upgrade everything'
    ],
    nixCommand: 'nixos-rebuild switch'
  },
  
  search: {
    patterns: [
      /^search\s+(?:for\s+)?(.+)$/i,
      /^find\s+(.+)$/i,
      /^what\'s?\s+(.+)$/i,
    ],
    examples: [
      'search firefox',
      'find browsers',
      'search for text editors',
      "what's available for python"
    ],
    nixCommand: 'nix search nixpkgs {query}'
  }
};

// Export type for pattern structure
export interface Pattern {
  patterns: RegExp[];
  examples: string[];
  nixCommand: string;
}
EOF
      ;;
    
    "personality")
      cat > packages/$pkg/src/index.ts << 'EOF'
// @nix-humanity/personality - Adaptive personality system

import type { PersonalityStyle } from '@nix-humanity/core';

export class PersonalityAdapter {
  private currentStyle: PersonalityStyle['name'] = 'friendly';
  
  adaptResponse(baseResponse: string, style?: PersonalityStyle['name']): string {
    // TODO: Implement style adaptation
    return baseResponse;
  }
  
  detectPreferredStyle(history: string[]): PersonalityStyle['name'] {
    // TODO: Implement style detection
    return 'friendly';
  }
}

export { styles } from './styles';
export { ResponseGenerator } from './response-generator';
EOF
      ;;
    
    "learning")
      cat > packages/$pkg/src/index.ts << 'EOF'
// @nix-humanity/learning - User preference learning system

import type { UserPreferences } from '@nix-humanity/core';

export class LearningSystem {
  async recordInteraction(command: string, success: boolean): Promise<void> {
    // TODO: Implement learning
  }
  
  async getPreferences(): Promise<UserPreferences> {
    // TODO: Implement preference retrieval
    throw new Error('Not implemented yet');
  }
}

export { PreferenceStore } from './preference-store';
export { PatternLearner } from './pattern-learner';
EOF
      ;;
    
    "ui")
      cat > packages/$pkg/src/index.ts << 'EOF'
// @nix-humanity/ui - User interfaces

export class CLI {
  async start(): Promise<void> {
    console.log('🗣️ Nix for Humanity - Natural Language NixOS Interface');
    console.log('Type your commands naturally, or say "help" to learn more.\n');
    
    // TODO: Implement CLI interface
  }
}

export { AdaptiveUI } from './adaptive-ui';
export { VoiceInterface } from './voice-interface';
export { Renderer } from './renderer';
EOF
      ;;
  esac
  
  # Create basic test file
  cat > packages/$pkg/test/index.test.js << EOF
import { test } from 'node:test';
import assert from 'node:assert';

test('$pkg module exports', async () => {
  const module = await import('../dist/index.js');
  assert.ok(module, 'Module should export something');
});
EOF

  # Create placeholder files for other exports
  touch packages/$pkg/src/{types,constants,utils}.ts 2>/dev/null || true
done

# Create specific subdirectories for complex packages
echo "📁 Creating subdirectories for complex packages..."

# NLP subdirectories
mkdir -p packages/nlp/src/{fuzzy-matcher,context-tracker,error-recovery}
touch packages/nlp/src/fuzzy-matcher/index.ts
touch packages/nlp/src/context-tracker/index.ts
touch packages/nlp/src/error-recovery/index.ts

# Executor subdirectories
mkdir -p packages/executor/src/{validator,sandbox,permissions}
touch packages/executor/src/validator/index.ts
touch packages/executor/src/sandbox/index.ts  
touch packages/executor/src/permissions/index.ts

# Create main entry point
echo "🚀 Creating main application entry point..."
cat > src/index.ts << 'EOF'
#!/usr/bin/env node

import { CLI } from '@nix-humanity/ui';

async function main() {
  const cli = new CLI();
  await cli.start();
}

main().catch(console.error);
EOF

# Create .gitignore
echo "📝 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
package-lock.json

# Build outputs
dist/
*.tsbuildinfo

# Logs
*.log
npm-debug.log*

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Test coverage
coverage/
.nyc_output/

# Temporary
tmp/
temp/
EOF

# Create development setup script
echo "🛠️  Creating development setup script..."
cat > setup-dev.sh << 'EOF'
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
EOF
chmod +x setup-dev.sh

echo ""
echo "✅ Modular architecture created successfully!"
echo ""
echo "📁 Structure created:"
echo "   packages/"
echo "   ├── core/        # Shared types, constants, utilities"
echo "   ├── nlp/         # Natural Language Processing"
echo "   ├── executor/    # Command execution engine"
echo "   ├── patterns/    # Pattern definitions (single source)"
echo "   ├── personality/ # Adaptive personality system"
echo "   ├── learning/    # User preference learning"
echo "   └── ui/          # User interfaces (CLI, Tauri)"
echo ""
echo "🚀 Next steps:"
echo "   1. Run: ./setup-dev.sh"
echo "   2. Start consolidating existing code into packages"
echo "   3. Build the MVP functionality"
echo ""
echo "We flow! 🌊"