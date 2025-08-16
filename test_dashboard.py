#!/usr/bin/env python3
"""
Test the real-time dashboard functionality.
"""

import asyncio
import sys
import os
sys.path.insert(0, 'src')

from luminous_nix.self_healing.dashboard import SimpleDashboard

async def test_simple_dashboard():
    """Test the simple dashboard"""
    print("🚀 Testing Simple Dashboard")
    print("=" * 40)
    
    dashboard = SimpleDashboard()
    
    # Run for 5 seconds
    try:
        await asyncio.wait_for(dashboard.run(), timeout=5)
    except asyncio.TimeoutError:
        print("\n✅ Dashboard ran successfully for 5 seconds")
    except Exception as e:
        print(f"\n❌ Dashboard error: {e}")


async def test_metrics_collection():
    """Test metrics collection"""
    print("\n📊 Testing Metrics Collection")
    print("=" * 40)
    
    from luminous_nix.self_healing.dashboard import MetricsDashboard
    
    dashboard = MetricsDashboard()
    
    # Get system metrics
    metrics = dashboard.get_system_metrics()
    
    print(f"\nSystem Metrics Collected:")
    if 'cpu' in metrics:
        print(f"  ✅ CPU: {metrics['cpu']['percent']:.1f}%")
    if 'memory' in metrics:
        print(f"  ✅ Memory: {metrics['memory']['percent']:.1f}%")
    if 'disk' in metrics:
        print(f"  ✅ Disk: {metrics['disk']['percent']:.1f}%")
    if 'processes' in metrics:
        print(f"  ✅ Processes: {metrics['processes']}")
    
    # Test sparkline creation
    test_data = [10, 20, 30, 25, 35, 40, 30, 20, 15, 25]
    sparkline = dashboard._create_sparkline(test_data)
    print(f"\n📈 Sparkline Test: {sparkline}")


async def test_rich_dashboard():
    """Test Rich dashboard if available"""
    try:
        import rich
        from luminous_nix.self_healing.dashboard import MetricsDashboard
        
        print("\n🎨 Testing Rich Dashboard")
        print("=" * 40)
        
        dashboard = MetricsDashboard()
        
        # Create panels
        metrics = dashboard.get_system_metrics()
        
        # Test panel creation
        header = dashboard.create_header_panel()
        system = dashboard.create_system_panel(metrics)
        healing = dashboard.create_healing_panel({})
        events = dashboard.create_events_panel()
        footer = dashboard.create_footer_panel()
        
        print("  ✅ Header panel created")
        print("  ✅ System panel created")
        print("  ✅ Healing panel created")
        print("  ✅ Events panel created")
        print("  ✅ Footer panel created")
        
        # Test layout
        layout = dashboard.create_layout()
        print("  ✅ Layout created successfully")
        
        return True
        
    except ImportError:
        print("\n⚠️ Rich library not available, skipping Rich dashboard test")
        return False


async def main():
    """Run all tests"""
    print("🌟 Luminous Nix Dashboard Test Suite")
    print("=" * 50)
    
    # Test metrics collection
    await test_metrics_collection()
    
    # Test Rich dashboard if available
    has_rich = await test_rich_dashboard()
    
    # Test simple dashboard briefly
    if not has_rich:
        await test_simple_dashboard()
    
    print("\n" + "=" * 50)
    print("✨ Dashboard tests completed!")
    print("\nTo run the full dashboard:")
    print("  ./bin/luminous-dashboard")
    print("\nOr with custom metrics URL:")
    print("  ./bin/luminous-dashboard http://localhost:9090/metrics")


if __name__ == "__main__":
    asyncio.run(main())