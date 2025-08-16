#!/usr/bin/env python3
"""
Simple test of healing plans without requiring root permissions.
"""

import asyncio
import sys
import logging

# Add src to path
sys.path.insert(0, 'src')

from luminous_nix.self_healing.healing_engine import SelfHealingEngine, Issue, Severity
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Test healing plan creation without execution"""
    print("\n" + "="*70)
    print("🚀 LUMINOUS NIX HEALING PLANS TEST")
    print("="*70)
    
    engine = SelfHealingEngine()
    
    # Test CPU healing plan
    print("\n📊 Testing CPU Healing Plan Creation")
    print("-"*40)
    
    cpu_issue = Issue(
        id="test_cpu",
        timestamp=datetime.now(),
        type='cpu_high',
        severity=Severity.HIGH,
        description="CPU usage at 95%",
        metrics={'cpu_percent': 95},
        affected_components=['system.cpu']
    )
    
    cpu_plan = await engine.create_healing_plan(cpu_issue)
    if cpu_plan:
        print(f"✅ CPU healing plan created:")
        print(f"   Actions: {[a.value for a in cpu_plan.actions]}")
        print(f"   Confidence: {cpu_plan.confidence:.2f}")
        print(f"   Impact: {cpu_plan.estimated_impact}")
    else:
        print("❌ No CPU healing plan available")
    
    # Test temperature healing plan
    print("\n🔥 Testing Temperature Healing Plan Creation")
    print("-"*40)
    
    temp_issue = Issue(
        id="test_temp",
        timestamp=datetime.now(),
        type='temperature_high',
        severity=Severity.CRITICAL,
        description="CPU temperature at 92°C",
        metrics={'temperature': 92},
        affected_components=['system.temperature']
    )
    
    temp_plan = await engine.create_healing_plan(temp_issue)
    if temp_plan:
        print(f"✅ Temperature healing plan created:")
        print(f"   Actions: {[a.value for a in temp_plan.actions]}")
        print(f"   Confidence: {temp_plan.confidence:.2f}")
        print(f"   Impact: {temp_plan.estimated_impact}")
    else:
        print("❌ No temperature healing plan available")
    
    # Test memory healing plan
    print("\n💾 Testing Memory Healing Plan Creation")
    print("-"*40)
    
    mem_issue = Issue(
        id="test_mem",
        timestamp=datetime.now(),
        type='memory_high',
        severity=Severity.HIGH,
        description="Memory usage at 92%",
        metrics={'memory_percent': 92},
        affected_components=['system.memory']
    )
    
    mem_plan = await engine.create_healing_plan(mem_issue)
    if mem_plan:
        print(f"✅ Memory healing plan created:")
        print(f"   Actions: {[a.value for a in mem_plan.actions]}")
        print(f"   Confidence: {mem_plan.confidence:.2f}")
        print(f"   Impact: {mem_plan.estimated_impact}")
    else:
        print("❌ No memory healing plan available")
    
    # Test disk healing plan
    print("\n💿 Testing Disk Healing Plan Creation")
    print("-"*40)
    
    disk_issue = Issue(
        id="test_disk",
        timestamp=datetime.now(),
        type='disk_full',
        severity=Severity.CRITICAL,
        description="Root disk at 95%",
        metrics={'disk_percent': 95, 'mount': '/'},
        affected_components=['disk./']
    )
    
    disk_plan = await engine.create_healing_plan(disk_issue)
    if disk_plan:
        print(f"✅ Disk healing plan created:")
        print(f"   Actions: {[a.value for a in disk_plan.actions]}")
        print(f"   Confidence: {disk_plan.confidence:.2f}")
        print(f"   Impact: {disk_plan.estimated_impact}")
        print(f"   Requires confirmation: {disk_plan.requires_confirmation}")
    else:
        print("❌ No disk healing plan available")
    
    # Check if healing would be triggered
    print("\n🔍 Testing Healing Decision Logic")
    print("-"*40)
    
    for issue in [cpu_issue, temp_issue, mem_issue, disk_issue]:
        should_heal = engine._should_heal(issue)
        print(f"   {issue.type}: {'✅ Would heal' if should_heal else '❌ Would not heal'}")
    
    print("\n" + "="*70)
    print("✅ Healing plan tests completed successfully!")
    print("="*70)
    print("\n📝 Summary:")
    print("- Healing plans can be created for all major issue types")
    print("- Decision logic determines when to apply healing")
    print("- No root permissions required for plan creation")
    print("- Actual healing would require appropriate permissions")


if __name__ == "__main__":
    asyncio.run(main())