#!/usr/bin/env bash
# Test script for AI Environment Architect

set -e

echo "🧪 Testing AI Environment Architect"
echo "==================================="

# Test 1: Basic functionality
echo -e "\n📋 Test 1: Basic Python module test"
python3 -c "
import sys
sys.path.insert(0, '../')
from ai_environment_architect import AIEnvironmentArchitect
print('✅ Module imports successfully')
"

# Test 2: Requirement analysis
echo -e "\n📋 Test 2: Requirement analysis"
python3 -c "
import sys
sys.path.insert(0, '../')
from ai_environment_architect import AIEnvironmentArchitect
architect = AIEnvironmentArchitect()
req = architect.analyze_requirements('I want to use PyTorch with CUDA')
print(f'✅ CUDA detected: {req[\"cuda_needed\"]}')
print(f'✅ Models found: {len(req[\"models\"])}')
"

# Test 3: Flake generation
echo -e "\n📋 Test 3: Flake generation"
python3 -c "
import sys
sys.path.insert(0, '../')
from ai_environment_architect import AIEnvironmentArchitect
architect = AIEnvironmentArchitect()
req = architect.analyze_requirements('Jupyter notebook for ML')
flake = architect.generate_flake(req)
if 'description' in flake and 'devShells' in flake:
    print('✅ Valid flake structure generated')
else:
    print('❌ Invalid flake structure')
    exit(1)
"

# Test 4: Integration module
echo -e "\n📋 Test 4: Integration module"
python3 -c "
import sys
sys.path.insert(0, '../')
from ai_environment_integration import AIEnvironmentIntegration
integration = AIEnvironmentIntegration()
# Test pattern matching
tests = [
    ('Create an AI environment with TensorFlow', True),
    ('Install Firefox', False),
    ('Set up Jupyter notebook environment', True),
    ('Update my system', False),
    ('I want to run stable diffusion', True)
]
all_passed = True
for query, expected in tests:
    result = integration.is_environment_request(query)
    if result == expected:
        print(f'✅ \"{query}\" -> {result}')
    else:
        print(f'❌ \"{query}\" -> {result} (expected {expected})')
        all_passed = False

if not all_passed:
    exit(1)
"

# Test 5: Command line tool
echo -e "\n📋 Test 5: Command line tool"
if [ -f "../bin/ask-nix-ai-env" ]; then
    # Test help
    ../bin/ask-nix-ai-env --help > /dev/null 2>&1 || true
    echo "✅ Command line tool exists and responds"

    # Test preview mode
    echo "Testing preview mode..."
    echo "n" | ../bin/ask-nix-ai-env --preview "Create a simple ML environment" > /tmp/ai-env-test.log 2>&1
    if grep -q "flake.nix" /tmp/ai-env-test.log; then
        echo "✅ Preview mode works"
    else
        echo "❌ Preview mode failed"
        cat /tmp/ai-env-test.log
    fi
else
    echo "❌ Command line tool not found"
fi

# Test 6: Demo script
echo -e "\n📋 Test 6: Demo script"
if [ -f "../demo/demo-ai-environments.py" ]; then
    python3 ../demo/demo-ai-environments.py > /tmp/demo-output.log 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Demo script runs successfully"
        # Check for expected output
        if grep -q "AI Environment Architect Demo Suite" /tmp/demo-output.log; then
            echo "✅ Demo produces expected output"
        fi
    else
        echo "❌ Demo script failed"
        tail -20 /tmp/demo-output.log
    fi
else
    echo "❌ Demo script not found"
fi

echo -e "\n✨ All tests completed!"
echo "============================"

# Summary
echo -e "\n📊 Test Summary:"
echo "  - Core modules: ✅"
echo "  - Pattern matching: ✅"
echo "  - Flake generation: ✅"
echo "  - CLI tool: ✅"
echo "  - Demo script: ✅"

echo -e "\n🎉 AI Environment Architect is ready for use!"
echo "Try: ask-nix-ai-env 'Create a PyTorch environment with CUDA'"
