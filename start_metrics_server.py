#!/usr/bin/env python3
"""
Standalone script to start the Prometheus metrics server for monitoring.

Usage:
    python start_metrics_server.py [--port PORT] [--host HOST]
"""

import asyncio
import sys
import signal
import argparse

# Add src to path
sys.path.insert(0, 'src')

from luminous_nix.self_healing.healing_engine import SelfHealingEngine

async def main(host='0.0.0.0', port=9191):
    """Run the metrics server with healing engine."""
    
    print("🚀 Starting Luminous Nix Metrics Server")
    print("=" * 50)
    
    # Create healing engine
    print("🔧 Initializing self-healing engine...")
    engine = SelfHealingEngine()
    
    # Start the engine
    print("✨ Starting monitoring systems...")
    await engine.start()
    
    # Start metrics server
    print(f"\n📊 Starting metrics server on {host}:{port}...")
    try:
        await engine.start_metrics_server(host=host, port=port)
        print("\n✅ Metrics server is running!")
        print(f"\n📍 Available endpoints:")
        print(f"   📊 Metrics:   http://{host if host != '0.0.0.0' else 'localhost'}:{port}/metrics")
        print(f"   🏥 Health:    http://{host if host != '0.0.0.0' else 'localhost'}:{port}/health")
        print(f"   🌐 Dashboard: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/")
        print(f"\n💡 Add to Prometheus configuration:")
        print(f"   scrape_configs:")
        print(f"     - job_name: 'luminous-nix'")
        print(f"       static_configs:")
        print(f"         - targets: ['localhost:{port}']")
        print(f"\n🛑 Press Ctrl+C to stop the server\n")
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(3600)
            
    except Exception as e:
        print(f"❌ Failed to start metrics server: {e}")
        await engine.stop()
        return 1
    
def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("\n\n🛑 Shutting down metrics server...")
    sys.exit(0)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Start Luminous Nix Prometheus Metrics Server')
    parser.add_argument('--port', type=int, default=9191, help='Port to listen on (default: 9191)')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    args = parser.parse_args()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the server
    try:
        asyncio.run(main(args.host, args.port))
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)