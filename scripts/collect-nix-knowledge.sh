#!/usr/bin/env bash

# Sacred Trinity Knowledge Collector
# Helps collect and organize NixOS knowledge from the local LLM

set -euo pipefail

KNOWLEDGE_DIR="${NIX_FOR_HUMANITY_ROOT:-$(pwd)}/docs/nix-knowledge"
DATE=$(date +%Y%m%d_%H%M%S)

# Ensure directories exist
mkdir -p "$KNOWLEDGE_DIR"/{questions,answers,examples}

# Function to ask and save
ask_and_save() {
    local question="$1"
    local category="${2:-general}"
    local filename=$(echo "$question" | tr ' ' '_' | tr -cd '[:alnum:]_' | cut -c1-50)

    echo "🤔 Asking: $question"
    echo

    # Save question
    echo "$question" > "$KNOWLEDGE_DIR/questions/${DATE}_${filename}.txt"

    # Get answer
    answer=$(ask-nix-guru "$question" 2>/dev/null || echo "Error getting answer")

    # Save answer
    {
        echo "Question: $question"
        echo "Category: $category"
        echo "Date: $(date)"
        echo "---"
        echo "$answer"
    } > "$KNOWLEDGE_DIR/answers/${DATE}_${filename}.md"

    echo "✅ Saved to: $KNOWLEDGE_DIR/answers/${DATE}_${filename}.md"
    echo
}

# Main menu
show_menu() {
    echo "🌟 Sacred Trinity Knowledge Collector"
    echo "===================================="
    echo "1. Ask about NixOS basics"
    echo "2. Ask about package management"
    echo "3. Ask about system configuration"
    echo "4. Ask about development practices"
    echo "5. Ask custom question"
    echo "6. View recent answers"
    echo "7. Exit"
    echo
}

# Predefined questions for common topics
BASICS_QUESTIONS=(
    "What makes NixOS different from other Linux distributions?"
    "How does Nix ensure reproducibility?"
    "What is a Nix derivation?"
    "Explain Nix profiles in simple terms"
    "What are NixOS generations?"
)

PACKAGE_QUESTIONS=(
    "What's the difference between nix-env and configuration.nix?"
    "How do I search for packages in NixOS?"
    "What are Nix channels?"
    "How do I install packages temporarily?"
    "What is an overlay in Nix?"
)

CONFIG_QUESTIONS=(
    "How do I structure my configuration.nix?"
    "What are NixOS modules?"
    "How do I manage secrets in NixOS?"
    "How do I create a custom systemd service?"
    "What is home-manager?"
)

DEV_QUESTIONS=(
    "How do I set up a development environment in NixOS?"
    "What is a Nix flake?"
    "How do I use direnv with Nix?"
    "What is a shell.nix file?"
    "How do I package software for NixOS?"
)

# Main loop
while true; do
    show_menu
    read -p "Choose an option: " choice

    case $choice in
        1)
            echo "📚 NixOS Basics Questions:"
            select q in "${BASICS_QUESTIONS[@]}" "Back"; do
                [[ "$q" == "Back" ]] && break
                [[ -n "$q" ]] && ask_and_save "$q" "basics"
            done
            ;;
        2)
            echo "📦 Package Management Questions:"
            select q in "${PACKAGE_QUESTIONS[@]}" "Back"; do
                [[ "$q" == "Back" ]] && break
                [[ -n "$q" ]] && ask_and_save "$q" "packages"
            done
            ;;
        3)
            echo "⚙️ System Configuration Questions:"
            select q in "${CONFIG_QUESTIONS[@]}" "Back"; do
                [[ "$q" == "Back" ]] && break
                [[ -n "$q" ]] && ask_and_save "$q" "configuration"
            done
            ;;
        4)
            echo "🛠️ Development Practice Questions:"
            select q in "${DEV_QUESTIONS[@]}" "Back"; do
                [[ "$q" == "Back" ]] && break
                [[ -n "$q" ]] && ask_and_save "$q" "development"
            done
            ;;
        5)
            read -p "Enter your question: " custom_q
            read -p "Category (default: custom): " category
            ask_and_save "$custom_q" "${category:-custom}"
            ;;
        6)
            echo "📖 Recent Answers:"
            ls -t "$KNOWLEDGE_DIR/answers/" | head -10
            echo
            read -p "Enter filename to view (or press Enter to skip): " filename
            [[ -n "$filename" ]] && less "$KNOWLEDGE_DIR/answers/$filename"
            ;;
        7)
            echo "👋 Thank you for building our knowledge base!"
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac

    echo
    read -p "Press Enter to continue..."
    clear
done
