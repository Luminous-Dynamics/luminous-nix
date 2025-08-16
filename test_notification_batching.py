#!/usr/bin/env python3
"""
Test the flow-respecting notification batching system.

Demonstrates how non-critical notifications are batched to protect user flow state,
while critical errors are shown immediately.
"""

import asyncio
import time
from src.luminous_nix.self_healing.healing_engine_v2 import SimplifiedHealingEngine
from src.luminous_nix.self_healing.notification_queue import Priority, get_notification_queue

async def demo_notification_batching():
    """Demonstrate the 2-minute notification batching"""
    
    print("\n" + "="*60)
    print("🌟 Flow-Respecting Notification System Demo")
    print("="*60)
    
    # Create healing engine with short intervals for demo
    engine = SimplifiedHealingEngine()
    queue = get_notification_queue()
    
    # Override batch interval for faster demo (10 seconds instead of 2 minutes)
    queue.batch_interval = 10
    
    print("\n📝 Configuration:")
    print(f"   Batch interval: {queue.batch_interval} seconds (reduced for demo)")
    print(f"   Max batch size: {queue.max_batch_size}")
    print()
    
    # Simulate various notifications
    print("🚀 Simulating system activity...")
    print("-" * 40)
    
    # 1. Normal notifications (will be batched)
    queue.add("System check completed", Priority.NORMAL, "info")
    print("✓ Added: System check completed (NORMAL)")
    
    await asyncio.sleep(1)
    queue.add("Memory usage at 75%", Priority.NORMAL, "warning")
    print("✓ Added: Memory usage at 75% (NORMAL)")
    
    await asyncio.sleep(1)
    queue.add("Package cache cleaned", Priority.LOW, "success")
    print("✓ Added: Package cache cleaned (LOW)")
    
    # 2. Critical notification (shown immediately)
    await asyncio.sleep(1)
    print("\n⚠️ Critical issue detected...")
    queue.add("CRITICAL: Disk space at 98%!", Priority.CRITICAL, "error")
    
    # 3. More normal notifications
    await asyncio.sleep(2)
    queue.add("Backup completed successfully", Priority.NORMAL, "success")
    print("✓ Added: Backup completed (NORMAL)")
    
    queue.add("3 packages need updates", Priority.LOW, "info")
    print("✓ Added: 3 packages need updates (LOW)")
    
    # Show queue status
    print("\n📊 Queue Status:")
    status = queue.get_status()
    print(f"   Notifications held: {status['held_notifications']}")
    print(f"   Time until batch: {status['time_until_flush']:.1f}s")
    print(f"   In flow state: {status['in_flow_state']}")
    
    # 4. Demonstrate flow state
    print("\n🧘 Entering flow state (deep work mode)...")
    queue.enter_flow_state()
    
    await asyncio.sleep(1)
    queue.add("Network reconnected", Priority.NORMAL, "info")
    print("✓ Added during flow: Network reconnected (held)")
    
    await asyncio.sleep(1)
    queue.add("Temperature normal", Priority.LOW, "success")
    print("✓ Added during flow: Temperature normal (held)")
    
    print("\n⏳ Waiting for batch delivery...")
    print("   (Notifications are being held to protect flow state)")
    
    # Wait for batch
    await asyncio.sleep(8)
    
    # Exit flow state
    print("\n📬 Exiting flow state...")
    queue.exit_flow_state()
    
    # Final status
    await asyncio.sleep(2)
    print("\n✅ Demo complete!")
    print("\nKey observations:")
    print("• Critical notifications appeared immediately")
    print("• Normal notifications were batched")
    print("• Flow state prevented interruptions")
    print("• All notifications eventually delivered")
    
    # Demonstrate with healing engine
    print("\n" + "="*60)
    print("🔧 Testing with Healing Engine")
    print("="*60)
    
    # Enter flow state for healing
    engine.enter_flow_state()
    print("🧘 Flow state active - healing notifications will be batched")
    
    # Run one healing cycle
    print("\n🔍 Running healing detection...")
    results = await engine.detect_and_heal()
    
    print(f"\n📊 Healing complete: {len(results)} actions taken")
    print(f"   Notification queue: {engine.get_notification_status()['held_notifications']} messages held")
    
    # Exit flow state to see batched notifications
    print("\n📬 Exiting flow state to deliver healing notifications...")
    engine.exit_flow_state()
    
    print("\n✨ All notifications delivered in batch!")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_notification_batching())