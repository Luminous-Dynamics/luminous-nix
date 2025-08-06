#!/usr/bin/env node

/**
 * Nix for Humanity - Simplified unified entry point
 * Natural language interface for NixOS
 */

const express = require('express');
const path = require('path');
const readline = require('readline');

// Import the best parts from each implementation
const { IntentRecognizer } = require('./implementations/web-based/js/nlp/intent-recognition');
const realExecutor = require('./implementations/nodejs-mvp/services/real-executor');

// Expand patterns from 10 to 50+ commands
const patterns = {
  // Package management
  install: [
    /^(install|get|add|setup)\s+(.+)$/i,
    /^i need\s+(.+)$/i,
    /^can you install\s+(.+)$/i
  ],
  remove: [
    /^(remove|uninstall|delete)\s+(.+)$/i,
    /^get rid of\s+(.+)$/i
  ],
  search: [
    /^(search|find|look for|what is)\s+(.+)$/i,
    /^is there a?n?\s+(.+)$/i
  ],
  update: [
    /^(update|upgrade)(\s+system)?$/i,
    /^keep (everything|system) up to date$/i
  ],
  // System management
  service: [
    /^(start|stop|restart|status)\s+(.+)(\s+service)?$/i,
    /^is\s+(.+)\s+running\?$/i
  ],
  // ... add more patterns
};

class NixForHumanity {
  constructor() {
    this.mode = process.argv.includes('--web') ? 'web' : 'cli';
    this.dryRun = process.argv.includes('--dry-run');
    this.port = process.env.PORT || 3000;
  }

  async processInput(input) {
    // Find matching pattern
    for (const [intent, patterns] of Object.entries(patterns)) {
      for (const pattern of patterns) {
        const match = input.match(pattern);
        if (match) {
          return this.executeIntent(intent, match);
        }
      }
    }
    
    return {
      success: false,
      message: "I don't understand that command. Try 'help' for examples."
    };
  }

  async executeIntent(intent, match) {
    try {
      // Extract the relevant part from the match
      const target = match[match.length - 1] || match[1];
      
      // Log what we're doing
      console.log(`📝 Intent: ${intent}, Target: ${target}`);
      
      // Execute with real executor
      const result = await realExecutor.execute(intent, [target]);
      
      return {
        success: result.success,
        message: result.success ? 
          `✅ ${this.getSuccessMessage(intent, target)}` :
          `❌ Failed: ${result.error}`,
        details: result.output,
        suggestion: result.suggestion
      };
    } catch (error) {
      return {
        success: false,
        message: `Error: ${error.message}`,
        suggestion: 'Try a simpler command or check the help'
      };
    }
  }

  getSuccessMessage(intent, target) {
    const messages = {
      install: `Installed ${target}`,
      remove: `Removed ${target}`,
      search: `Found results for ${target}`,
      update: 'System updated',
      service: `Service command executed for ${target}`
    };
    return messages[intent] || 'Command completed';
  }

  startCLI() {
    console.log('🚀 Nix for Humanity - Natural Language Interface for NixOS');
    console.log('Type your commands naturally. Type "exit" to quit.\n');

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: '> '
    });

    rl.prompt();

    rl.on('line', async (line) => {
      if (line.trim() === 'exit') {
        console.log('👋 Goodbye!');
        process.exit(0);
      }

      const result = await this.processInput(line.trim());
      console.log(result.message);
      if (result.details) console.log('\nDetails:', result.details);
      if (result.suggestion) console.log('\n💡 Suggestion:', result.suggestion);
      console.log('');
      
      rl.prompt();
    });
  }

  startWeb() {
    const app = express();
    app.use(express.json());
    app.use(express.static(path.join(__dirname, 'public')));

    app.post('/api/process', async (req, res) => {
      const { input } = req.body;
      const result = await this.processInput(input);
      res.json(result);
    });

    app.listen(this.port, () => {
      console.log(`🌐 Nix for Humanity web interface running at http://localhost:${this.port}`);
      console.log(`${this.dryRun ? '🏃 Running in DRY RUN mode' : '⚡ Running in REAL mode'}`);
    });
  }

  start() {
    if (this.dryRun) {
      process.env.DRY_RUN = 'true';
      console.log('🏃 Running in DRY RUN mode - no real commands will be executed\n');
    }

    if (this.mode === 'web') {
      this.startWeb();
    } else {
      this.startCLI();
    }
  }
}

// Start the application
const app = new NixForHumanity();
app.start();