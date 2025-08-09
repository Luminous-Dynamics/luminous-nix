#!/usr/bin/env python3
"""Test script to verify enhanced backend integration with CLI"""
import os
import sys
import subprocess

# Set environment variables
os.environ['NIX_HUMANITY_PYTHON_BACKEND'] = 'true'
os.environ['NIX_HUMANITY_ENHANCED'] = 'true'
os.environ['DEBUG'] = 'true'

print("🧪 Testing Enhanced Backend Integration with CLI")
print("=" * 50)

# Test 1: Check if backend is accessible
print("\n1. Checking backend accessibility...")
try:
    backend_path = os.path.join(os.path.dirname(__file__))
    sys.path.insert(0, backend_path)
    
    # Fix imports by adding parent directory
    parent_path = os.path.dirname(backend_path)
    if parent_path not in sys.path:
        sys.path.insert(0, parent_path)
    
    from nix_humanity.core.engine import NixForHumanityBackend
    from nix_humanity.api.schema import Request
    
    print("✅ Backend modules imported successfully")
    
    # Test backend initialization
    backend = NixForHumanityBackend()
    print("✅ Native backend initialized")
    
except Exception as e:
    print(f"❌ Backend import failed: {e}")
    sys.exit(1)

# Test 2: Direct backend test
print("\n2. Testing direct backend operation...")
try:
    request = Request(
        query="list generations",
        context={
            'frontend': 'cli',
            'dry_run': True
        }
    )
    
    response = backend.process(request)
    print(f"✅ Backend response: {response.success}")
    if response.text:
        print(f"   Response preview: {response.text[:100]}...")
        
except Exception as e:
    print(f"❌ Backend operation failed: {e}")

# Test 3: CLI integration test
print("\n3. Testing CLI integration...")
cli_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bin', 'ask-nix')

if os.path.exists(cli_path):
    try:
        result = subprocess.run(
            [sys.executable, cli_path, "list generations"],
            capture_output=True,
            text=True,
            timeout=10,
            env=os.environ
        )
        
        print(f"   Exit code: {result.returncode}")
        
        # Check for backend indicators
        if "Using Python backend" in result.stdout or "Using Python backend" in result.stderr:
            print("✅ Python backend detected in output")
        else:
            print("⚠️  Python backend not detected in output")
            
        if "enhanced backend" in result.stdout.lower() or "enhanced backend" in result.stderr.lower():
            print("✅ Enhanced backend message found")
        else:
            print("⚠️  Enhanced backend message not found")
            
        print(f"\n   Output preview: {result.stdout[:200]}...")
        
    except subprocess.TimeoutExpired:
        print("❌ CLI command timed out")
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
else:
    print(f"❌ CLI not found at {cli_path}")

print("\n" + "=" * 50)
print("Test complete!")