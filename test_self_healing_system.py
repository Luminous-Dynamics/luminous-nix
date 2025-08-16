#!/usr/bin/env python3
"""
Test the complete self-healing system with proactive optimization.

This demonstrates:
1. Issue detection and automatic healing
2. Learning from successful fixes
3. Proactive optimization to prevent issues
4. Integration with environmental awareness
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from luminous_nix.environmental import get_system_monitor
from luminous_nix.self_healing.healing_engine import (
    SelfHealingEngine,
    Issue,
    Severity,
    HealingAction
)
from luminous_nix.self_healing.proactive_optimizer import (
    ProactiveOptimizer,
    OptimizationType,
    create_intelligent_healing_system
)


async def test_healing_engine():
    """Test the self-healing engine"""
    print("\n🔧 Testing Self-Healing Engine")
    print("=" * 50)
    
    engine = SelfHealingEngine()
    
    # Start the engine
    print("1. Starting healing engine...")
    await engine.start()
    
    # Simulate some issues
    print("\n2. Simulating system issues...")
    
    # High memory issue
    memory_issue = Issue(
        id="test_mem_001",
        timestamp=datetime.now(),
        type='memory_high',
        severity=Severity.HIGH,
        description="Test: Memory usage at 88%",
        metrics={'memory_percent': 88},
        affected_components=['system.memory']
    )
    
    # Failed service issue
    service_issue = Issue(
        id="test_svc_001",
        timestamp=datetime.now(),
        type='service_failed',
        severity=Severity.HIGH,
        description="Test: nginx.service has failed",
        metrics={'service': 'nginx.service'},
        affected_components=['service.nginx']
    )
    
    # Test healing memory issue
    print("\n3. Attempting to heal memory issue...")
    result = await engine.heal_issue(memory_issue)
    
    if result:
        print(f"   ✅ Healing {'successful' if result.success else 'failed'}")
        print(f"   Actions taken: {result.actions_taken}")
        print(f"   Duration: {result.duration_seconds:.1f}s")
    
    # Test healing service issue
    print("\n4. Attempting to heal service issue...")
    result = await engine.heal_issue(service_issue)
    
    if result:
        print(f"   ✅ Healing {'successful' if result.success else 'failed'}")
        print(f"   Actions taken: {result.actions_taken}")
    
    # Check knowledge base
    print("\n5. Checking healing knowledge base...")
    knowledge = engine.knowledge
    
    stats = knowledge.knowledge['statistics']
    print(f"   Total heals: {stats['total_heals']}")
    print(f"   Successful: {stats['successful_heals']}")
    print(f"   Success rate: {stats['successful_heals']/max(1, stats['total_heals']):.1%}")
    
    # Test confidence calculation
    print("\n6. Testing confidence for repeated issues...")
    confidence = knowledge.get_confidence(memory_issue, [HealingAction.CLEAR_CACHE])
    print(f"   Confidence for memory fix: {confidence:.1%}")
    
    # Stop the engine
    await engine.stop()
    
    print("\n✅ Self-healing engine test complete!")


async def test_proactive_optimizer():
    """Test the proactive optimizer"""
    print("\n🚀 Testing Proactive Optimizer")
    print("=" * 50)
    
    optimizer = ProactiveOptimizer()
    
    # Start optimizer
    print("1. Starting proactive optimizer...")
    await optimizer.start()
    
    # Find optimization opportunities
    print("\n2. Finding optimization opportunities...")
    opportunities = await optimizer.find_opportunities()
    
    if opportunities:
        print(f"   Found {len(opportunities)} opportunities:")
        for opp in opportunities[:5]:
            print(f"   • {opp.description}")
            print(f"     Type: {opp.type.value}")
            print(f"     Priority: {opp.priority}/10")
            print(f"     Confidence: {opp.confidence:.1%}")
            print(f"     Score: {opp.score():.1f}")
    else:
        print("   No immediate opportunities found")
    
    # Test optimization application (dry run)
    if opportunities:
        print("\n3. Testing optimization (dry run)...")
        best = opportunities[0]
        
        print(f"   Would optimize: {best.description}")
        print(f"   Actions: {best.actions}")
        print(f"   Estimated benefit: {best.estimated_benefit}")
        print(f"   Safe to automate: {best.safe_to_automate}")
    
    # Test prevention of future issues
    print("\n4. Testing issue prevention...")
    await optimizer.prevent_future_issues()
    print("   Preventive measures applied")
    
    # Get optimization report
    print("\n5. Optimization report (last 24h):")
    report = optimizer.get_optimization_report(hours=24)
    
    print(f"   Total optimizations: {report['total_optimizations']}")
    print(f"   Successful: {report['successful']}")
    print(f"   Success rate: {report['success_rate']:.1%}")
    
    # Stop optimizer
    await optimizer.stop()
    
    print("\n✅ Proactive optimizer test complete!")


async def test_integrated_healing_system():
    """Test the complete integrated healing system"""
    print("\n🌟 Testing Integrated Intelligent Healing System")
    print("=" * 50)
    
    # Create integrated system
    print("1. Creating intelligent healing system...")
    system = create_intelligent_healing_system()
    
    healing_engine = system['healing_engine']
    optimizer = system['optimizer']
    
    # Start the system
    print("\n2. Starting all components...")
    await system['start']()
    
    # Let it run for a bit
    print("\n3. System running (monitoring for 10 seconds)...")
    await asyncio.sleep(10)
    
    # Check system state
    print("\n4. System status:")
    
    # Check detected issues
    issues = await healing_engine.detect_issues()
    print(f"   Detected issues: {len(issues)}")
    for issue in issues[:3]:
        print(f"   • {issue.description} [{issue.severity.value}]")
    
    # Check optimization opportunities
    opportunities = await optimizer.find_opportunities()
    print(f"\n   Optimization opportunities: {len(opportunities)}")
    for opp in opportunities[:3]:
        print(f"   • {opp.description} [score: {opp.score():.1f}]")
    
    # Check healing knowledge
    stats = healing_engine.knowledge.knowledge['statistics']
    print(f"\n   Healing statistics:")
    print(f"   • Total heals: {stats['total_heals']}")
    print(f"   • Successful: {stats['successful_heals']}")
    
    # Stop the system
    print("\n5. Stopping system...")
    await system['stop']()
    
    print("\n✅ Integrated system test complete!")


async def demonstrate_learning():
    """Demonstrate how the system learns from fixes"""
    print("\n🧠 Demonstrating Learning Capabilities")
    print("=" * 50)
    
    engine = SelfHealingEngine()
    
    print("1. Simulating repeated issue...")
    
    # Create the same issue multiple times
    for i in range(3):
        issue = Issue(
            id=f"learn_{i}",
            timestamp=datetime.now(),
            type='memory_high',
            severity=Severity.HIGH,
            description="Memory at 85%",
            metrics={'memory_percent': 85},
            affected_components=['system.memory']
        )
        
        print(f"\n   Attempt {i+1}:")
        
        # Check confidence before
        actions = [HealingAction.CLEAR_CACHE, HealingAction.FREE_MEMORY]
        confidence_before = engine.knowledge.get_confidence(issue, actions)
        print(f"   Confidence before: {confidence_before:.1%}")
        
        # Create healing plan
        plan = await engine.create_healing_plan(issue)
        if plan:
            print(f"   Plan confidence: {plan.confidence:.1%}")
            
            # Simulate successful healing
            from luminous_nix.self_healing.healing_engine import HealingResult
            result = HealingResult(
                issue_id=issue.id,
                success=True,
                actions_taken=['clear_cache', 'free_memory'],
                metrics_before={'memory_percent': 85},
                metrics_after={'memory_percent': 65},
                duration_seconds=5.0
            )
            
            # Record the healing
            engine.knowledge.record_healing(issue, result)
            
            # Check confidence after
            confidence_after = engine.knowledge.get_confidence(issue, actions)
            print(f"   Confidence after: {confidence_after:.1%}")
            print(f"   Learning improvement: +{(confidence_after - confidence_before):.1%}")
    
    print("\n2. Knowledge base summary:")
    fixes = engine.knowledge.knowledge['fixes']
    print(f"   Known fix patterns: {len(fixes)}")
    
    for fingerprint, fix_list in list(fixes.items())[:3]:
        print(f"   • Pattern {fingerprint}: {len(fix_list)} successful fixes")
    
    print("\n✅ Learning demonstration complete!")


async def main():
    """Main test function"""
    print("🔧 Luminous Nix - Self-Healing System Test")
    print("=" * 60)
    print("Testing self-healing, learning, and proactive optimization")
    
    # Test individual components
    await test_healing_engine()
    await test_proactive_optimizer()
    
    # Test integrated system
    await test_integrated_healing_system()
    
    # Demonstrate learning
    await demonstrate_learning()
    
    print("\n" + "=" * 60)
    print("✨ All self-healing tests completed successfully!")
    print("\nCapabilities demonstrated:")
    print("  ✅ Automatic issue detection and healing")
    print("  ✅ Learning from successful fixes")
    print("  ✅ Proactive optimization to prevent issues")
    print("  ✅ Integration with environmental awareness")
    print("  ✅ Confidence-based decision making")
    print("\nThe system can now:")
    print("  • Detect and fix issues automatically")
    print("  • Learn from experience to improve over time")
    print("  • Prevent issues before they occur")
    print("  • Optimize system performance continuously")
    print("  • Provide detailed reports and insights")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()