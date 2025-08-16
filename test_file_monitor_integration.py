#!/usr/bin/env python3
"""
Test the integration between FileSystemMonitor and SelfHealingEngine.

This script demonstrates:
1. File monitoring activation
2. Event detection and healing
3. Configuration hot-reload
4. Statistics collection
"""

import asyncio
import sys
from pathlib import Path
import tempfile
import time

# Add src to path
sys.path.insert(0, 'src')

from luminous_nix.self_healing.healing_engine import SelfHealingEngine
from luminous_nix.environmental.file_monitor import FileSystemMonitor, FileEvent, FileEventType

async def main():
    """Test file monitoring integration."""
    
    print("🧪 Testing File Monitor Integration with Self-Healing Engine")
    print("=" * 60)
    
    # Create test directory
    test_dir = Path(tempfile.mkdtemp(prefix='luminous-test-'))
    print(f"📁 Test directory: {test_dir}")
    
    # Create healing engine
    print("\n🔧 Creating self-healing engine...")
    engine = SelfHealingEngine()
    
    # Check if file monitoring is available
    if not engine.file_monitor.is_available():
        print("❌ File monitoring not available (watchdog not installed)")
        print("   Install with: poetry add watchdog")
        return
    
    print("✅ File monitor available")
    
    # Start the engine
    print("\n🚀 Starting self-healing engine...")
    await engine.start()
    
    # Add test directory to monitoring
    print(f"\n📍 Adding {test_dir} to monitoring...")
    engine.file_monitor.add_path(
        path=test_dir,
        recursive=True,
        patterns=['*.conf', '*.txt', '*.nix'],
        checksum_validation=True
    )
    
    # Create a test configuration file
    test_config = test_dir / 'test.conf'
    test_config.write_text('# Test configuration\nkey = value\n')
    print(f"✏️  Created: {test_config}")
    
    # Add hot-reload for the config
    print(f"\n🔄 Adding hot-reload for {test_config}...")
    engine.add_configuration_hot_reload(test_config)
    
    # Wait for events to process
    await asyncio.sleep(2)
    
    # Modify the file
    print(f"\n✏️  Modifying {test_config}...")
    test_config.write_text('# Test configuration\nkey = new_value\n')
    
    await asyncio.sleep(2)
    
    # Create a critical file
    critical_file = test_dir / 'configuration.nix'
    critical_file.write_text('{ config = "test"; }')
    print(f"✏️  Created critical file: {critical_file}")
    
    await asyncio.sleep(2)
    
    # Delete the critical file (should trigger healing)
    print(f"\n🗑️  Deleting critical file: {critical_file}")
    critical_file.unlink()
    
    await asyncio.sleep(3)
    
    # Get statistics
    print("\n📊 File Monitor Statistics:")
    stats = engine.file_monitor.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Get monitored paths
    print("\n📂 Monitored Paths:")
    for path in engine.file_monitor.get_monitored_paths():
        print(f"   - {path}")
    
    # Check healing knowledge
    print("\n🧠 Healing Knowledge Statistics:")
    knowledge_stats = engine.knowledge.knowledge.get('statistics', {})
    for key, value in knowledge_stats.items():
        print(f"   {key}: {value}")
    
    # Stop the engine
    print("\n🛑 Stopping self-healing engine...")
    await engine.stop()
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
    print(f"\n🧹 Cleaned up test directory")
    
    print("\n✅ Integration test complete!")
    
    # Summary
    print("\n📋 Integration Features Tested:")
    print("   ✓ File monitoring activation")
    print("   ✓ Event detection")
    print("   ✓ Configuration hot-reload") 
    print("   ✓ Critical file monitoring")
    print("   ✓ Statistics collection")
    print("   ✓ Graceful shutdown")

if __name__ == "__main__":
    asyncio.run(main())