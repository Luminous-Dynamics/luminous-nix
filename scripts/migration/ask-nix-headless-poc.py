#!/usr/bin/env python3
"""
Proof of Concept: Integrating Headless Engine into ask-nix
This shows how to add headless engine support with feature flags
while maintaining backward compatibility.
"""

import os
import sys
from pathlib import Path

# Add scripts directory to path
script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
sys.path.insert(0, script_dir)

# Feature flag for headless engine
USE_HEADLESS_ENGINE = os.getenv('NIX_USE_HEADLESS', 'false').lower() == 'true'

print(f"🔧 Headless Engine: {'ENABLED' if USE_HEADLESS_ENGINE else 'DISABLED'}")

if USE_HEADLESS_ENGINE:
    print("✅ Using new headless architecture")
    try:
        from core.headless_engine import HeadlessEngine, Context, ExecutionMode
        from adapters.cli_adapter import CLIAdapter
        HEADLESS_AVAILABLE = True
    except ImportError as e:
        print(f"⚠️  Headless engine not available: {e}")
        print("Falling back to legacy implementation")
        HEADLESS_AVAILABLE = False
        USE_HEADLESS_ENGINE = False
else:
    print("📦 Using legacy implementation")
    HEADLESS_AVAILABLE = False

# Import legacy components (always needed for fallback)
from nix_knowledge_engine import NixOSKnowledgeEngine

class HybridNixAssistant:
    """
    Hybrid implementation that can use either legacy or headless engine
    based on feature flag and availability.
    """
    
    def __init__(self):
        self.use_headless = USE_HEADLESS_ENGINE and HEADLESS_AVAILABLE
        
        if self.use_headless:
            print("🚀 Initializing headless engine...")
            self.adapter = CLIAdapter(use_server=False)
            self.execution_mode = ExecutionMode.SAFE
        else:
            print("📚 Initializing legacy components...")
            self.knowledge = NixOSKnowledgeEngine()
            # Other legacy components would be initialized here
            
    def process_query(self, query: str, personality: str = 'friendly'):
        """Process a query using either headless or legacy engine"""
        
        if self.use_headless:
            # Use headless engine
            context = Context(
                personality=personality,
                execution_mode=self.execution_mode,
                collect_feedback=True,
                capabilities=['text']
            )
            
            response = self.adapter.process_query(query, context)
            
            # Convert headless response to legacy format if needed
            return {
                'text': response.get('text', ''),
                'intent': response.get('intent', {}),
                'commands': response.get('commands', []),
                'success': True
            }
        else:
            # Use legacy implementation
            intent = self.knowledge.extract_intent(query)
            solution = self.knowledge.get_solution(intent)
            response_text = self.knowledge.format_response(intent, solution)
            
            return {
                'text': response_text,
                'intent': intent,
                'commands': [],  # Would extract from solution
                'success': solution.get('found', False)
            }
    
    def get_engine_info(self):
        """Get information about which engine is being used"""
        return {
            'headless_available': HEADLESS_AVAILABLE,
            'use_headless': self.use_headless,
            'engine_type': 'headless' if self.use_headless else 'legacy',
            'feature_flag': USE_HEADLESS_ENGINE
        }

def demonstrate_compatibility():
    """Demonstrate that both engines produce compatible results"""
    
    assistant = HybridNixAssistant()
    
    # Test queries
    test_queries = [
        "How do I install Firefox?",
        "Update my system",
        "My WiFi isn't working"
    ]
    
    print("\n📊 Engine Information:")
    info = assistant.get_engine_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n🧪 Testing Queries:")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        response = assistant.process_query(query)
        
        print(f"✅ Success: {response['success']}")
        print(f"🎯 Intent: {response['intent'].get('action', 'unknown')}")
        print(f"💬 Response Preview: {response['text'][:100]}...")
        
        if response.get('commands'):
            print(f"📦 Commands: {len(response['commands'])} found")
    
    print("\n" + "=" * 60)
    print("✨ Compatibility test complete!")

def compare_engines():
    """Compare performance between legacy and headless engines"""
    
    import time
    
    print("\n⚡ Performance Comparison")
    print("=" * 60)
    
    # Force legacy engine
    os.environ['NIX_USE_HEADLESS'] = 'false'
    legacy_assistant = HybridNixAssistant()
    
    # Force headless engine (if available)
    os.environ['NIX_USE_HEADLESS'] = 'true'
    headless_assistant = HybridNixAssistant()
    
    query = "install firefox and vscode"
    
    # Time legacy
    start = time.time()
    legacy_response = legacy_assistant.process_query(query)
    legacy_time = time.time() - start
    
    # Time headless
    if headless_assistant.use_headless:
        start = time.time()
        headless_response = headless_assistant.process_query(query)
        headless_time = time.time() - start
        
        print(f"Legacy Engine: {legacy_time:.3f}s")
        print(f"Headless Engine: {headless_time:.3f}s")
        print(f"Speedup: {legacy_time/headless_time:.2f}x")
    else:
        print("Headless engine not available for comparison")

if __name__ == "__main__":
    print("🔬 Nix for Humanity - Headless Engine Integration POC")
    print("=" * 60)
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--compare":
        compare_engines()
    else:
        demonstrate_compatibility()
    
    print("\n💡 Try running with different configurations:")
    print("  NIX_USE_HEADLESS=false python ask-nix-headless-poc.py")
    print("  NIX_USE_HEADLESS=true python ask-nix-headless-poc.py")
    print("  python ask-nix-headless-poc.py --compare")