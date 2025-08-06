#!/usr/bin/env node

/**
 * Nix for Humanity - Unified Implementation
 * Bringing together the best of our implementations
 */

const readline = require('readline');
const express = require('express');
const path = require('path');

// Use our real executor instead of mocks
const realExecutor = require('./implementations/nodejs-mvp/services/real-executor');

// Import comprehensive patterns and enhanced NLP engine
const { patterns: nlpPatterns, matchPattern } = require('./src/nlp/quick-start-patterns');
const EnhancedNLPEngine = require('./src/nlp/enhanced-nlp-engine');

// Extend with additional patterns for help and other commands
const extendedPatterns = {
  ...nlpPatterns,
  
  // Add help patterns
  'help': [
    /^help$/i,
    /^what can you do\??$/i,
    /^show commands$/i,
    /^how do i (.+)$/i
  ],
  
  // Add list patterns (not in quick-start)
  'package.list': [
    /^(list|show)(\s+installed)?(\s+packages)?$/i,
    /^what('s| is) installed\??$/i,
    /^show me what i have$/i
  ],
  
  // Add rollback patterns
  'system.rollback': [
    /^rollback$/i,
    /^go back$/i,
    /^undo (?:the )?(?:last )?update$/i
  ],
  
  // Add garbage collection
  'system.gc': [
    /^clean(?:up)?(?:\s+system)?$/i,
    /^free (?:up )?space$/i,
    /^garbage collect$/i
  ]
};

class NixForHumanity {
  constructor() {
    this.mode = process.argv.includes('--web') ? 'web' : 'cli';
    this.dryRun = process.argv.includes('--dry-run');
    this.port = process.env.PORT || 3000;
    
    // Initialize enhanced NLP engine
    this.nlpEngine = new EnhancedNLPEngine();
    
    // Set dry run in environment for executor
    if (this.dryRun) {
      process.env.DRY_RUN = 'true';
    }
  }

  async processInput(input) {
    const trimmed = input.trim().toLowerCase();
    
    // Special commands
    if (trimmed === 'exit' || trimmed === 'quit') {
      return { exit: true };
    }
    
    // Use the enhanced NLP engine
    const nlpResult = await this.nlpEngine.processInput(input);
    
    // Check if we have a good result from the enhanced engine
    if (nlpResult.result) {
      // Handle category requests
      if (nlpResult.result.type === 'category_request') {
        return this.handleCategoryRequest(nlpResult.result);
      }
      
      // Pass enhanced result to executeIntent
      return this.executeIntent(nlpResult.result.intent, nlpResult.result);
    }
    
    // If no match, check if we had corrections
    if (nlpResult.hadCorrections) {
      return {
        success: false,
        message: `I tried to understand "${nlpResult.processed}" but couldn't find a match. Try 'help' for examples.`,
        suggestion: nlpResult.contextSuggestions && nlpResult.contextSuggestions.length > 0 ? 
          nlpResult.contextSuggestions[0] : null
      };
    }
    
    // Fall back to extended patterns (for help and other special commands)
    for (const [intent, patternList] of Object.entries(extendedPatterns)) {
      for (const pattern of patternList) {
        const match = input.match(pattern);
        if (match) {
          return this.executeIntent(intent, match);
        }
      }
    }
    
    return {
      success: false,
      message: "I don't understand that command. Try 'help' for examples.",
      suggestions: nlpResult.contextSuggestions
    };
  }

  handleCategoryRequest(result) {
    const { category, suggestions, message, fullList } = result;
    
    let response = `${message}\n`;
    suggestions.forEach((pkg, index) => {
      response += `  ${index + 1}. ${pkg}\n`;
    });
    
    response += `\nYou can install any of these by saying "install ${suggestions[0]}" for example.`;
    
    return {
      success: true,
      message: response,
      suggestions: fullList
    };
  }
  
  async executeIntent(intent, match) {
    try {
      // Special handling for help
      if (intent === 'help') {
        return this.showHelp();
      }
      
      // Handle NLP match format vs regex match format
      let target = '';
      let commandIntent = intent;
      let packageInfo = null;
      
      if (match.entities) {
        // NLP match format
        target = match.entities.package || match.entities.service || '';
        commandIntent = intent.replace('.', '_'); // Convert package.install to package_install
        packageInfo = match.packageInfo;
      } else {
        // Regex match format
        target = match[match.length - 1] || match[1] || '';
      }
      
      // Show package resolution info if available
      if (packageInfo && packageInfo.confidence < 1.0) {
        console.log(`\n🔍 Resolved: "${target}" → "${packageInfo.resolved}" (${packageInfo.reason})`);
        if (packageInfo.alternatives && packageInfo.alternatives.length > 0) {
          console.log(`   Alternatives: ${packageInfo.alternatives.join(', ')}`);
        }
      }
      
      console.log(`\n📝 Understanding: ${intent}${target ? ` ${target}` : ''}`);
      
      // Map intents to executor commands
      const commandMap = {
        'package_install': 'install',
        'package_remove': 'remove',
        'package_search': 'search',
        'package_list': 'list',
        'system_update': 'update',
        'system_rollback': 'rollback',
        'system_gc': 'gc',
        'system_info': 'info',
        'service_start': 'restart',
        'service_stop': 'stop',
        'service_status': 'status'
      };
      
      const command = commandMap[commandIntent] || commandIntent;
      
      // Execute with real executor
      const result = await realExecutor.execute(command, target ? [target] : []);
      
      // Track result with NLP engine for learning
      const executionResult = {
        success: result.success,
        message: result.success ? 
          `✅ ${this.getSuccessMessage(command, target)}` :
          `❌ Failed: ${result.error || 'Unknown error'}`,
        details: result.output,
        suggestion: result.suggestion,
        error: result.error,
        package: target
      };
      
      // Let the NLP engine learn from the result
      const enhancedResult = await this.nlpEngine.handleExecutionResult(
        match.original || match[0],
        intent,
        executionResult
      );
      
      return enhancedResult || executionResult;
    } catch (error) {
      return {
        success: false,
        message: `Error: ${error.message}`,
        suggestion: 'Try a simpler command or check the help'
      };
    }
  }
  
  showHelp() {
    const helpText = `
🌟 Nix for Humanity - Natural Language Commands

📦 Package Management:
  • "install firefox" - Install a package
  • "remove firefox" - Remove a package
  • "search browser" - Search for packages
  • "list installed" - Show installed packages

🔧 System:
  • "update system" - Update NixOS
  • "show running services" - List services
  
💡 Examples:
  • "I need a text editor"
  • "Can you install git?"
  • "What's installed?"
  • "Get rid of vim"
  
Type 'exit' to quit.
`;
    
    return {
      success: true,
      message: helpText
    };
  }

  getSuccessMessage(intent, target) {
    const messages = {
      install: `Installing ${target}...`,
      remove: `Removing ${target}...`,
      search: `Searching for ${target}...`,
      update: 'Updating system...',
      list: 'Listing installed packages...',
      rollback: 'Rolling back to previous generation...',
      gc: 'Cleaning up old packages...',
      info: 'Getting system information...',
      restart: `Restarting ${target}...`,
      stop: `Stopping ${target}...`,
      status: `Checking status of ${target}...`
    };
    return messages[intent] || 'Command executed';
  }

  startCLI() {
    console.log('🚀 Nix for Humanity - Natural Language Interface for NixOS');
    console.log('Type your commands naturally. Type "help" for examples or "exit" to quit.');
    console.log('✨ Features: Typo correction, context awareness, package aliases, and learning!\n');
    
    if (this.dryRun) {
      console.log('🏃 Running in DRY RUN mode - no real commands will be executed\n');
    }

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: '> '
    });

    rl.prompt();

    rl.on('line', async (line) => {
      const result = await this.processInput(line.trim());
      
      if (result.exit) {
        console.log('\n👋 Goodbye!');
        process.exit(0);
      }
      
      console.log(result.message);
      if (result.details) {
        console.log('\nOutput:', result.details);
      }
      if (result.suggestion) {
        console.log('\n💡 Suggestion:', result.suggestion);
      }
      if (result.suggestions && Array.isArray(result.suggestions)) {
        console.log('\n💡 Suggestions:');
        result.suggestions.forEach(sugg => {
          if (typeof sugg === 'string') {
            console.log(`   • ${sugg}`);
          } else if (sugg.suggestion) {
            console.log(`   • ${sugg.suggestion}`);
            if (sugg.actions) {
              sugg.actions.forEach(action => console.log(`     - ${action}`));
            }
          }
        });
      }
      if (result.errorAnalysis) {
        console.log('\n🔍 Error Analysis:', result.errorAnalysis.message);
        if (result.errorAnalysis.suggestion) {
          console.log('   Try:', result.errorAnalysis.suggestion);
        }
      }
      if (result.recovery && result.recovery.length > 0) {
        console.log('\n🔧 Recovery Options:');
        result.recovery.forEach((option, index) => {
          console.log(`   ${index + 1}. ${option.message}`);
        });
      }
      console.log('');
      
      rl.prompt();
    });
  }

  startWeb() {
    const app = express();
    app.use(express.json());
    app.use(express.static(path.join(__dirname, 'public')));

    app.get('/', (req, res) => {
      res.send(`
        <html>
          <head>
            <title>Nix for Humanity</title>
            <style>
              body { font-family: system-ui; max-width: 800px; margin: 0 auto; padding: 20px; }
              h1 { color: #2563eb; }
              #chat { border: 1px solid #e5e7eb; padding: 20px; height: 400px; overflow-y: auto; }
              #input { width: 100%; padding: 10px; margin-top: 10px; }
              button { padding: 10px 20px; background: #2563eb; color: white; border: none; cursor: pointer; }
            </style>
          </head>
          <body>
            <h1>🚀 Nix for Humanity</h1>
            <div id="chat"></div>
            <input type="text" id="input" placeholder="Type your command naturally..." />
            <button onclick="sendCommand()">Send</button>
            
            <script>
              async function sendCommand() {
                const input = document.getElementById('input');
                const chat = document.getElementById('chat');
                const command = input.value;
                
                if (!command) return;
                
                chat.innerHTML += '<div><strong>You:</strong> ' + command + '</div>';
                input.value = '';
                
                const response = await fetch('/api/process', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ input: command })
                });
                
                const result = await response.json();
                chat.innerHTML += '<div><strong>Nix:</strong> ' + result.message + '</div>';
                if (result.details) {
                  chat.innerHTML += '<div><em>Details:</em> <pre>' + result.details + '</pre></div>';
                }
                chat.scrollTop = chat.scrollHeight;
              }
              
              document.getElementById('input').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendCommand();
              });
            </script>
          </body>
        </html>
      `);
    });

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