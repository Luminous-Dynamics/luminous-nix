#!/usr/bin/env python3
"""
Test the Prometheus metrics server for the self-healing engine.

This script demonstrates:
1. Starting the metrics server
2. Exposing Prometheus metrics
3. Health endpoint functionality
4. Web dashboard
"""

import asyncio
import sys
import aiohttp

# Add src to path
sys.path.insert(0, 'src')

from luminous_nix.self_healing.healing_engine import SelfHealingEngine

async def test_endpoints(base_url: str = "http://localhost:9191"):
    """Test the various endpoints."""
    async with aiohttp.ClientSession() as session:
        # Test metrics endpoint
        print("\n📊 Testing /metrics endpoint...")
        try:
            async with session.get(f"{base_url}/metrics") as resp:
                if resp.status == 200:
                    text = await resp.text()
                    # Check for some expected metrics
                    if "luminous_nix" in text:
                        print("✅ Metrics endpoint working!")
                        print("   Sample metrics found:")
                        for line in text.split('\n')[:10]:
                            if line and not line.startswith('#'):
                                print(f"   - {line[:80]}")
                else:
                    print(f"❌ Metrics endpoint returned status {resp.status}")
        except Exception as e:
            print(f"❌ Failed to fetch metrics: {e}")
        
        # Test health endpoint
        print("\n🏥 Testing /health endpoint...")
        try:
            async with session.get(f"{base_url}/health") as resp:
                if resp.status in [200, 503]:  # Can be unhealthy
                    data = await resp.json()
                    print(f"✅ Health endpoint working!")
                    print(f"   Status: {'Healthy' if data['healthy'] else 'Unhealthy'}")
                    print(f"   System Health: {data['system_health']}%")
                    print(f"   Files Monitored: {data['files_monitored']}")
                    print(f"   Issues Healed: {data['issues_healed']}")
                else:
                    print(f"❌ Health endpoint returned status {resp.status}")
        except Exception as e:
            print(f"❌ Failed to fetch health: {e}")
        
        # Test dashboard
        print("\n🌐 Testing / (dashboard) endpoint...")
        try:
            async with session.get(base_url) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    if "Luminous Nix" in text:
                        print("✅ Dashboard endpoint working!")
                        print(f"   Visit {base_url} in your browser to see the dashboard")
                else:
                    print(f"❌ Dashboard returned status {resp.status}")
        except Exception as e:
            print(f"❌ Failed to fetch dashboard: {e}")

async def main():
    """Test the Prometheus metrics server."""
    
    print("🧪 Testing Prometheus Metrics Server")
    print("=" * 60)
    
    # Create healing engine
    print("\n🔧 Creating self-healing engine...")
    engine = SelfHealingEngine()
    
    # Start the engine
    print("🚀 Starting self-healing engine...")
    await engine.start()
    
    # Start metrics server on a different port
    port = 9191  # Use different port to avoid conflicts
    print(f"\n📊 Starting metrics server on port {port}...")
    try:
        await engine.start_metrics_server(host='0.0.0.0', port=port)
        print("✅ Metrics server started successfully!")
    except Exception as e:
        print(f"❌ Failed to start metrics server: {e}")
        await engine.stop()
        return
    
    # Give it a moment to start
    await asyncio.sleep(2)
    
    # Test the endpoints
    await test_endpoints()
    
    # Print Prometheus configuration
    print("\n📝 Prometheus Configuration:")
    print("Add this to your prometheus.yml:")
    print("""
scrape_configs:
  - job_name: 'luminous-nix'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:9191']
        labels:
          service: 'self-healing'
          environment: 'production'
    """)
    
    # Print Grafana query examples
    print("\n📈 Example Grafana Queries:")
    print("""
1. System Health:
   luminous_nix_system_health_score

2. Issues Detected:
   rate(luminous_nix_healing_issues_detected_total[5m])

3. Healing Success Rate:
   rate(luminous_nix_healing_success_total[5m]) / 
   rate(luminous_nix_healing_attempts_total[5m])

4. File Events:
   luminous_nix_file_events_total

5. Memory Usage Trend:
   rate(luminous_nix_system_memory_used_bytes[5m])
    """)
    
    print("\n🌟 Metrics server is running!")
    print(f"   📊 Metrics: http://localhost:{port}/metrics")
    print(f"   🏥 Health: http://localhost:{port}/health")
    print(f"   🌐 Dashboard: http://localhost:{port}/")
    print("\nPress Ctrl+C to stop...")
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(60)
            # Could periodically print stats here
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
    
    # Cleanup
    await engine.stop_metrics_server()
    await engine.stop()
    print("✅ Shutdown complete!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")