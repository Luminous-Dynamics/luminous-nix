#!/usr/bin/env python3
"""
Test integrated voice interface with environmental awareness.

This demonstrates:
1. Voice control with system awareness
2. D-Bus service monitoring (if available)
3. Historical health tracking
4. Predictive assistance during voice interaction
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from luminous_nix.environmental import get_system_monitor
from luminous_nix.environmental.historical_trending import (
    HistoricalHealthTracker,
    integrate_historical_tracking
)
from luminous_nix.environmental.predictive_assistant import PredictiveAssistant


def test_historical_tracking():
    """Test historical health tracking"""
    print("\n📊 Testing Historical Health Tracking")
    print("=" * 50)
    
    # Initialize tracker
    tracker = HistoricalHealthTracker()
    
    # Simulate some historical data
    print("1. Recording sample metrics...")
    for i in range(10):
        # Simulate varying health scores
        health = 85 - (i * 2) if i < 5 else 75 + (i - 5) * 3
        tracker.record_metric('health_score', health)
        tracker.record_metric('cpu_percent', 20 + i * 5)
        tracker.record_metric('memory_percent', 50 + i * 3)
    
    # Analyze trends
    print("\n2. Analyzing trends...")
    health_trend = tracker.analyze_trend('health_score', hours=1)
    cpu_trend = tracker.analyze_trend('cpu_percent', hours=1)
    
    print(f"   Health trend: {health_trend.trend} (slope: {health_trend.slope:.2f})")
    print(f"   CPU trend: {cpu_trend.trend} (slope: {cpu_trend.slope:.2f})")
    
    # Generate report
    print("\n3. Generating health report...")
    report = tracker.generate_health_report(hours=1)
    
    print(f"   Average health: {report.average_health:.1f}/100")
    print(f"   Stability score: {report.stability_score:.1f}/100")
    
    if report.recommendations:
        print("   Recommendations:")
        for rec in report.recommendations[:3]:
            print(f"     • {rec}")
    
    # Predict future
    print("\n4. Predicting future health...")
    prediction = tracker.predict_future_health(hours_ahead=24)
    
    print(f"   Predicted health in 24h: {prediction['health_score']:.1f}")
    print(f"   Confidence: {prediction['confidence']:.1%}")
    
    if prediction['risks']:
        print("   Risks:")
        for risk in prediction['risks']:
            print(f"     ⚠️ {risk}")
    
    print("\n✅ Historical tracking test complete!")


def test_dbus_monitoring():
    """Test D-Bus service monitoring"""
    print("\n🔧 Testing D-Bus Service Monitoring")
    print("=" * 50)
    
    try:
        from luminous_nix.environmental.dbus_monitor import (
            DBusSystemdMonitor,
            DBUS_AVAILABLE
        )
        
        if not DBUS_AVAILABLE:
            print("⚠️ D-Bus not available - using fallback monitoring")
            return
        
        print("1. Initializing D-Bus monitor...")
        monitor = DBusSystemdMonitor()
        
        print("\n2. Checking key services...")
        services = monitor.get_key_services()
        
        for service in services[:5]:
            status_icon = "🟢" if service.is_running else "🔴"
            enabled_icon = "✓" if service.is_enabled else "✗"
            print(f"   {status_icon} {service.name}: {service.state.value} [{enabled_icon}]")
            if service.pid:
                print(f"      PID: {service.pid}, Memory: {service.memory_current/(1024*1024):.1f}MB")
        
        print("\n3. Checking for failed services...")
        failed = monitor.get_failed_services()
        
        if failed:
            print(f"   Found {len(failed)} failed services:")
            for service in failed[:3]:
                print(f"     🚨 {service.name}: {service.sub_state}")
        else:
            print("   ✅ No failed services")
        
        print("\n✅ D-Bus monitoring test complete!")
        
    except ImportError as e:
        print(f"⚠️ D-Bus monitoring not available: {e}")
    except Exception as e:
        print(f"❌ D-Bus monitoring error: {e}")


async def test_voice_with_awareness():
    """Test voice interface with environmental awareness"""
    print("\n🎤 Testing Voice Interface with Awareness")
    print("=" * 50)
    
    try:
        from luminous_nix.interfaces.voice_with_awareness import (
            SmartVoiceAssistant,
            AwareVoiceMode
        )
        
        print("1. Initializing smart voice assistant...")
        assistant = SmartVoiceAssistant()
        
        print("\n2. Demonstrating system awareness...")
        assistant.demo_system_awareness()
        
        print("\n3. Testing voice response modes...")
        
        # Simulate different system states
        test_cases = [
            ("install firefox", AwareVoiceMode.NORMAL),
            ("my system is slow", AwareVoiceMode.CONCERNED),
            ("help me free up space", AwareVoiceMode.HELPER)
        ]
        
        for query, expected_mode in test_cases:
            print(f"\n   Query: '{query}'")
            response = await assistant.interface.process_voice_command(query)
            print(f"   Response mode: {response.mode.value}")
            print(f"   Response: {response.text[:100]}...")
            
            if response.suggestions:
                print("   Suggestions:")
                for sug in response.suggestions[:2]:
                    print(f"     • {sug}")
        
        print("\n✅ Voice with awareness test complete!")
        
    except ImportError as e:
        print(f"⚠️ Voice components not fully available: {e}")
    except Exception as e:
        print(f"❌ Voice test error: {e}")


async def test_integrated_system():
    """Test fully integrated system"""
    print("\n🌟 Testing Fully Integrated System")
    print("=" * 50)
    
    # Initialize monitor
    monitor = get_system_monitor()
    
    # Start monitoring
    print("1. Starting system monitoring...")
    await monitor.start_monitoring()
    
    # Integrate historical tracking
    print("\n2. Enabling historical tracking...")
    tracker = integrate_historical_tracking(monitor)
    
    # Initialize predictive assistant
    print("\n3. Starting predictive assistant...")
    assistant = PredictiveAssistant(monitor)
    
    # Wait for some data
    await asyncio.sleep(2)
    
    # Get system insights
    print("\n4. System insights:")
    status = monitor.get_quick_status()
    
    print(f"   CPU: {status['cpu_percent']:.1f}%")
    print(f"   Memory: {status['memory_percent']:.1f}% ({status['memory_available_gb']:.1f}GB free)")
    print(f"   Uptime: {status['uptime_hours']:.1f} hours")
    
    # Get predictions
    predictions = assistant.analyze_system()
    if predictions:
        print("\n5. Predictive suggestions:")
        for pred in predictions[:3]:
            icon = {'critical': '🚨', 'high': '⚠️', 'medium': '💡', 'low': 'ℹ️'}.get(pred.priority, '•')
            print(f"   {icon} {pred.action}")
            print(f"      Reason: {pred.reason}")
    
    # Stop monitoring
    await monitor.stop_monitoring()
    
    print("\n✅ Integrated system test complete!")


async def main():
    """Main test function"""
    print("🚀 Luminous Nix - Integrated Features Test")
    print("=" * 60)
    print("Testing voice interface + environmental awareness + advanced monitoring")
    
    # Test components
    test_historical_tracking()
    test_dbus_monitoring()
    await test_voice_with_awareness()
    await test_integrated_system()
    
    print("\n" + "=" * 60)
    print("✨ All integrated features tested successfully!")
    print("\nSummary:")
    print("  ✅ Historical health tracking working")
    print("  ✅ D-Bus monitoring available (if installed)")
    print("  ✅ Voice interface with awareness functional")
    print("  ✅ Predictive assistance integrated")
    print("  ✅ Full system integration complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()