#!/usr/bin/env python3
"""
Simple test of environmental awareness features.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from luminous_nix.environmental import (
    SystemMonitor,
    PredictiveAssistant,
    ContextAwareIntentRecognizer
)

def main():
    print("🌟 Luminous Nix Environmental Awareness Demo\n")
    
    # Initialize monitor
    print("1. Collecting System State...")
    monitor = SystemMonitor()
    
    # Get current state
    state = monitor.get_state()
    if not state:
        # Collect fresh state
        import asyncio
        loop = asyncio.new_event_loop()
        loop.run_until_complete(monitor.update_category('cpu'))
        loop.run_until_complete(monitor.update_category('memory'))
        loop.run_until_complete(monitor.update_category('disk'))
        state = monitor.get_state()
    
    # Show quick status
    status = monitor.get_quick_status()
    print("\n📊 System Status:")
    print(f"  CPU: {status['cpu_percent']:.1f}%")
    print(f"  Memory: {status['memory_percent']:.1f}% ({status['memory_available_gb']:.1f}GB free)")
    print(f"  Load: {status['load_average'][0]:.2f}, {status['load_average'][1]:.2f}, {status['load_average'][2]:.2f}")
    
    for mount, percent in status.get('disk_usage', {}).items():
        icon = "🟢" if percent < 80 else "🟡" if percent < 90 else "🔴"
        print(f"  Disk {mount}: {percent:.1f}% {icon}")
    
    print(f"  Uptime: {status['uptime_hours']:.1f} hours")
    
    # Get predictions
    print("\n2. Analyzing System for Predictions...")
    assistant = PredictiveAssistant(monitor)
    predictions = assistant.analyze_system()
    
    if predictions:
        print("\n🔮 Predictive Suggestions:")
        for i, pred in enumerate(predictions[:3], 1):
            icon = {'critical': '🚨', 'high': '⚠️', 'medium': '💡', 'low': 'ℹ️'}.get(pred.priority, '•')
            print(f"\n{i}. {icon} {pred.action}")
            print(f"   Reason: {pred.reason}")
            print(f"   Confidence: {pred.confidence*100:.0f}%")
            if pred.data and 'command' in pred.data:
                print(f"   Command: {pred.data['command']}")
    else:
        print("\n✅ No issues detected - system is healthy!")
    
    # Test intent recognition
    print("\n3. Testing Context-Aware Intent Recognition...")
    recognizer = ContextAwareIntentRecognizer(monitor)
    
    test_queries = [
        "my system is slow",
        "free up some space",
        "install firefox",
        "what's wrong with my computer?"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        intent = recognizer.recognize(query)
        
        print(f"   Intent: {intent.intent_type.value} (confidence: {intent.confidence:.2f})")
        
        if intent.suggestions:
            print("   Suggestions:")
            for suggestion in intent.suggestions[:2]:
                print(f"     • {suggestion}")
        
        if intent.warnings:
            print("   ⚠️ Warnings:")
            for warning in intent.warnings:
                print(f"     • {warning}")
        
        # Show context if system issue detected
        if intent.context and ('cpu_usage' in intent.context or 'memory_usage' in intent.context):
            print("   Context considered:")
            if 'cpu_usage' in intent.context:
                print(f"     • CPU at {intent.context['cpu_usage']:.1f}%")
            if 'memory_usage' in intent.context:
                print(f"     • Memory at {intent.context['memory_usage']:.1f}%")
    
    # Show system health score
    print("\n4. System Health Assessment")
    
    # Simple health score calculation
    health_score = 100
    if status['memory_percent'] > 80:
        health_score -= 20
    elif status['memory_percent'] > 70:
        health_score -= 10
    
    if status['cpu_percent'] > 80:
        health_score -= 15
    elif status['cpu_percent'] > 70:
        health_score -= 5
    
    for percent in status.get('disk_usage', {}).values():
        if percent > 90:
            health_score -= 15
        elif percent > 80:
            health_score -= 5
    
    health_score = max(0, health_score)
    
    if health_score >= 90:
        health_icon = "🟢"
        health_text = "Excellent"
    elif health_score >= 70:
        health_icon = "🟡"
        health_text = "Good"
    elif health_score >= 50:
        health_icon = "🟠"
        health_text = "Fair"
    else:
        health_icon = "🔴"
        health_text = "Needs Attention"
    
    print(f"\n   Overall Health Score: {health_score}/100 {health_icon}")
    print(f"   Status: {health_text}")
    
    # Save snapshot
    snapshot_path = monitor.save_snapshot()
    print(f"\n📸 System snapshot saved to: {snapshot_path}")
    
    print("\n✨ Environmental Awareness Demo Complete!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()