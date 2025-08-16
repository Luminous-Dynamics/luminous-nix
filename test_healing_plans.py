#!/usr/bin/env python3
"""
Test the healing plans to ensure they work correctly.
"""

import asyncio
import sys
import logging

# Add src to path
sys.path.insert(0, 'src')

from luminous_nix.self_healing.healing_plans import HealingPlans
from luminous_nix.self_healing.healing_engine import SelfHealingEngine, Issue, Severity
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_cpu_healing():
    """Test CPU healing plan"""
    print("\n" + "="*50)
    print("🔧 Testing CPU Healing Plan")
    print("="*50)
    
    plans = HealingPlans()
    
    # Test with high CPU
    context = {
        'cpu_percent': 95,
        'temperature': 85
    }
    
    print(f"\n📊 Context: CPU at {context['cpu_percent']}%, Temp at {context['temperature']}°C")
    print("🔧 Executing healing plan...")
    
    result = await plans.heal_high_cpu(context)
    
    print(f"\n✅ Result: {'Success' if result['success'] else 'Failed'}")
    print(f"📝 Actions taken: {result['actions_taken']}")
    print(f"💬 Message: {result['message']}")
    
    return result['success']


async def test_temperature_healing():
    """Test temperature healing plan"""
    print("\n" + "="*50)
    print("🔥 Testing Temperature Healing Plan")
    print("="*50)
    
    plans = HealingPlans()
    
    # Test with high temperature
    context = {
        'temperature': 92,
        'cpu_percent': 75
    }
    
    print(f"\n📊 Context: Temperature at {context['temperature']}°C")
    print("🔧 Executing healing plan...")
    
    result = await plans.heal_high_temperature(context)
    
    print(f"\n✅ Result: {'Success' if result['success'] else 'Failed'}")
    print(f"📝 Actions taken: {result['actions_taken']}")
    print(f"💬 Message: {result['message']}")
    
    return result['success']


async def test_memory_healing():
    """Test memory healing plan"""
    print("\n" + "="*50)
    print("💾 Testing Memory Healing Plan")
    print("="*50)
    
    plans = HealingPlans()
    
    # Test with high memory
    context = {
        'memory_percent': 88
    }
    
    print(f"\n📊 Context: Memory at {context['memory_percent']}%")
    print("🔧 Executing healing plan...")
    
    result = await plans.heal_high_memory(context)
    
    print(f"\n✅ Result: {'Success' if result['success'] else 'Failed'}")
    print(f"📝 Actions taken: {result['actions_taken']}")
    print(f"💬 Message: {result['message']}")
    
    return result['success']


async def test_engine_integration():
    """Test integration with healing engine"""
    print("\n" + "="*50)
    print("🔧 Testing Healing Engine Integration")
    print("="*50)
    
    engine = SelfHealingEngine()
    
    # Create a test issue
    issue = Issue(
        id="test_cpu_1",
        timestamp=datetime.now(),
        type='cpu_high',
        severity=Severity.HIGH,
        description="Test CPU issue at 95%",
        metrics={'cpu_percent': 95},
        affected_components=['system.cpu']
    )
    
    print(f"\n📊 Issue: {issue.description}")
    print("🔧 Creating healing plan...")
    
    # Create healing plan
    plan = await engine.create_healing_plan(issue)
    
    if plan:
        print(f"✅ Plan created:")
        print(f"   Actions: {[a.value for a in plan.actions]}")
        print(f"   Confidence: {plan.confidence:.2f}")
        print(f"   Requires confirmation: {plan.requires_confirmation}")
    else:
        print("❌ No plan available")
    
    return plan is not None


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🚀 LUMINOUS NIX HEALING PLANS TEST SUITE")
    print("="*70)
    
    results = []
    
    # Test individual healing plans
    try:
        results.append(("CPU Healing", await test_cpu_healing()))
    except Exception as e:
        print(f"❌ CPU healing test failed: {e}")
        results.append(("CPU Healing", False))
    
    try:
        results.append(("Temperature Healing", await test_temperature_healing()))
    except Exception as e:
        print(f"❌ Temperature healing test failed: {e}")
        results.append(("Temperature Healing", False))
    
    try:
        results.append(("Memory Healing", await test_memory_healing()))
    except Exception as e:
        print(f"❌ Memory healing test failed: {e}")
        results.append(("Memory Healing", False))
    
    try:
        results.append(("Engine Integration", await test_engine_integration()))
    except Exception as e:
        print(f"❌ Engine integration test failed: {e}")
        results.append(("Engine Integration", False))
    
    # Print summary
    print("\n" + "="*70)
    print("📊 TEST RESULTS SUMMARY")
    print("="*70)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    
    print("\n" + "-"*70)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Healing plans are working correctly.")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please review the output above.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)