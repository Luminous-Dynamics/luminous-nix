#!/usr/bin/env bash
# Collect usage data from ask-trinity for continuous learning

set -e

KNOWLEDGE_DIR="/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/docs/nix-knowledge"
USAGE_DIR="$KNOWLEDGE_DIR/usage"
FEEDBACK_DIR="$KNOWLEDGE_DIR/feedback"

# Create directories
mkdir -p "$USAGE_DIR" "$FEEDBACK_DIR"

echo "📊 Sacred Trinity Usage Collector"
echo "================================="
echo
echo "This script helps collect real usage data to improve our models."
echo

# Function to save interaction
save_interaction() {
    local timestamp=$(date +%s.%N)
    local question="$1"
    local model="$2"
    local response="$3"
    local rating="$4"
    local correction="$5"
    
    # Save interaction
    cat > "$USAGE_DIR/interaction_$timestamp.json" << EOF
{
    "timestamp": "$timestamp",
    "date": "$(date -Iseconds)",
    "question": "$question",
    "model": "$model",
    "response": "$response",
    "rating": $rating,
    "correction": "$correction"
}
EOF
    
    # If highly rated, add to training data
    if [ "$rating" -ge 4 ]; then
        echo "$question" > "$KNOWLEDGE_DIR/questions/q_usage_$timestamp.txt"
        echo "$response" > "$KNOWLEDGE_DIR/answers/a_usage_$timestamp.txt"
        echo "✅ Added to training data"
    fi
    
    # If correction provided, save as better answer
    if [ -n "$correction" ]; then
        echo "$question" > "$KNOWLEDGE_DIR/questions/q_corrected_$timestamp.txt"
        echo "$correction" > "$KNOWLEDGE_DIR/answers/a_corrected_$timestamp.txt"
        echo "✅ Correction saved for training"
    fi
}

# Interactive collection mode
if [ "$1" = "--interactive" ]; then
    while true; do
        echo
        read -p "Enter your NixOS question (or 'quit' to exit): " question
        
        if [ "$question" = "quit" ]; then
            break
        fi
        
        # Get response from ask-trinity
        echo
        echo "🤖 Getting response..."
        response=$(ask-trinity "$question" 2>&1)
        echo
        echo "$response"
        echo
        
        # Get feedback
        read -p "Rate this response (1-5, 5 being perfect): " rating
        
        if [ "$rating" -lt 4 ]; then
            echo "Please provide a better answer (press Ctrl+D when done):"
            correction=$(cat)
        else
            correction=""
        fi
        
        # Extract model used from response
        model=$(echo "$response" | grep -oP "Using \K\w+" || echo "unknown")
        
        # Save interaction
        save_interaction "$question" "$model" "$response" "$rating" "$correction"
        
        echo
        echo "Thank you! Your feedback helps improve the models."
    done
    
    echo
    echo "📊 Collection complete!"
    echo "Run 'python3 sacred-trinity-trainer-v2.py' to retrain with new data."
    exit 0
fi

# Batch import mode
if [ "$1" = "--import" ] && [ -f "$2" ]; then
    echo "📥 Importing Q&A pairs from $2..."
    
    while IFS='|' read -r question answer; do
        timestamp=$(date +%s.%N)
        echo "$question" > "$KNOWLEDGE_DIR/questions/q_import_$timestamp.txt"
        echo "$answer" > "$KNOWLEDGE_DIR/answers/a_import_$timestamp.txt"
        sleep 0.01  # Ensure unique timestamps
    done < "$2"
    
    echo "✅ Import complete!"
    exit 0
fi

# Show usage statistics
if [ "$1" = "--stats" ]; then
    echo "📊 Usage Statistics"
    echo "==================="
    echo
    echo "Total interactions: $(ls -1 $USAGE_DIR/interaction_*.json 2>/dev/null | wc -l)"
    echo "Highly rated (4-5): $(grep -l '"rating": [45]' $USAGE_DIR/*.json 2>/dev/null | wc -l)"
    echo "Corrections provided: $(grep -l '"correction": "[^"]' $USAGE_DIR/*.json 2>/dev/null | wc -l)"
    echo
    echo "Questions in training data: $(ls -1 $KNOWLEDGE_DIR/questions/q_*.txt 2>/dev/null | wc -l)"
    echo "Answers in training data: $(ls -1 $KNOWLEDGE_DIR/answers/a_*.txt 2>/dev/null | wc -l)"
    exit 0
fi

# Default: Show help
echo "Usage:"
echo "  $0 --interactive    Interactive collection mode"
echo "  $0 --import FILE    Import Q&A pairs from file (format: question|answer)"
echo "  $0 --stats          Show usage statistics"
echo
echo "Examples:"
echo "  $0 --interactive"
echo "  $0 --import nixos-qa-pairs.txt"
echo "  $0 --stats"