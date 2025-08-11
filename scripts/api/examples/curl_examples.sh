#!/bin/bash
# Curl examples for testing the Nix for Humanity API

# Base URL
API_URL="http://localhost:5000"

echo "🧪 Nix for Humanity API Test Examples"
echo "=====================================\n"

# 1. Health check
echo "1. Health Check:"
curl -s "$API_URL/api/v1/health" | jq .
echo "\n---\n"

# 2. Get capabilities
echo "2. API Capabilities:"
curl -s "$API_URL/api/v1/capabilities" | jq .
echo "\n---\n"

# 3. Simple query
echo "3. Simple Query - Install Firefox:"
curl -s -X POST "$API_URL/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I install Firefox?",
    "context": {
      "personality": "friendly"
    }
  }' | jq .
echo "\n---\n"

# 4. Query with different personality
echo "4. Minimal Personality - Update System:"
curl -s -X POST "$API_URL/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Update my system",
    "context": {
      "personality": "minimal",
      "execution_mode": "dry_run"
    }
  }' | jq .
echo "\n---\n"

# 5. Symbiotic personality
echo "5. Symbiotic Personality - Complex Query:"
curl -s -X POST "$API_URL/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "My WiFi isnt working after update",
    "context": {
      "personality": "symbiotic",
      "capabilities": ["text", "visual"]
    }
  }' | jq .
echo "\n---\n"

# 6. Package search
echo "6. Search for Python Packages:"
curl -s "$API_URL/api/v1/search?q=python&limit=5" | jq .
echo "\n---\n"

# 7. Submit feedback
echo "7. Submit Positive Feedback:"
curl -s -X POST "$API_URL/api/v1/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "query": "How do I install Firefox?",
    "response": "Here is how to install Firefox...",
    "helpful": true,
    "rating": 5
  }' | jq .
echo "\n---\n"

# 8. Get statistics
echo "8. Engine Statistics:"
curl -s "$API_URL/api/v1/stats" | jq .
echo "\n---\n"

# 9. Visual capabilities query
echo "9. Query with Visual Response:"
curl -s -X POST "$API_URL/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me how to install VS Code",
    "context": {
      "personality": "encouraging",
      "capabilities": ["text", "visual"],
      "execution_mode": "learning"
    }
  }' | jq .
echo "\n---\n"

# 10. Error handling test
echo "10. Error Handling - Empty Query:"
curl -s -X POST "$API_URL/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": ""
  }' | jq .
echo "\n---\n"

echo "✅ Test examples complete!"
echo "Note: Install 'jq' for pretty JSON output: nix-env -iA nixos.jq"
