#!/usr/bin/env python3
"""
Demo script for AI Environment Architect
Shows various AI/ML environment generation examples
"""

import os
import sys

# Add parent scripts directory to path
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, script_dir)

from ai_environment_architect import AIEnvironmentArchitect
from ai_environment_integration import AIEnvironmentIntegration


def demo_basic_analysis():
    """Demo basic requirement analysis"""
    print("=" * 60)
    print("🔍 AI Environment Architect - Requirement Analysis Demo")
    print("=" * 60)

    architect = AIEnvironmentArchitect()

    test_requests = [
        "I want to experiment with transformers and need CUDA support",
        "Set up a Jupyter notebook for data science with pandas and scikit-learn",
        "I need to run Llama 2 locally on my machine",
        "Create a stable diffusion environment for generating art",
        "Machine learning development environment with TensorFlow",
        "I want to build a chatbot with langchain and local LLMs",
    ]

    for request in test_requests:
        print(f"\n📝 Request: {request}")
        requirements = architect.analyze_requirements(request)

        print("\n📊 Analysis:")
        print(f"  - Models detected: {len(requirements['models'])}")
        for tier, model, info in requirements["models"]:
            print(f"    • {info['description']} [{tier}]")
        print(f"  - CUDA needed: {'Yes' if requirements['cuda_needed'] else 'No'}")
        print(
            f"  - Experimental packages: {'Yes' if requirements['experimental'] else 'No'}"
        )
        print(f"  - Estimated RAM: {requirements['estimated_ram']}")
        print("-" * 60)


def demo_flake_generation():
    """Demo flake.nix generation"""
    print("\n" + "=" * 60)
    print("📄 Flake.nix Generation Demo")
    print("=" * 60)

    architect = AIEnvironmentArchitect()

    # Example 1: Pure Nix approach
    print("\n1️⃣ Pure Nix Environment (scikit-learn):")
    print("-" * 40)

    request = "Create a data science environment with Jupyter and scikit-learn"
    requirements = architect.analyze_requirements(request)
    flake = architect.generate_flake(requirements, "data-science")

    # Show first 30 lines
    lines = flake.split("\n")
    for i, line in enumerate(lines[:30]):
        print(f"{i+1:3} | {line}")
    print(f"... ({len(lines)-30} more lines)\n")

    # Example 2: Hybrid approach with pip
    print("2️⃣ Hybrid Environment (Llama + LangChain):")
    print("-" * 40)

    request = "I want to run Llama locally with langchain for RAG applications"
    requirements = architect.analyze_requirements(request)
    flake = architect.generate_flake(requirements, "llm-rag")

    # Show shellHook section
    lines = flake.split("\n")
    in_shellhook = False
    for line in lines:
        if "shellHook" in line:
            in_shellhook = True
        if in_shellhook:
            print(line)
            if line.strip() == "};":
                break


def demo_integration():
    """Demo the full integration flow"""
    print("\n" + "=" * 60)
    print("🔗 Full Integration Demo")
    print("=" * 60)

    integration = AIEnvironmentIntegration()

    queries = [
        "Create a PyTorch environment with CUDA for deep learning",
        "I need stable diffusion for my art project called sd-art",
        "Set up TensorFlow environment",
    ]

    for query in queries:
        print(f"\n🎯 Processing: {query}")

        if integration.is_environment_request(query):
            response = integration.handle_environment_request(query)

            print("\n📦 What will be created:")
            print(response["preview"])

            print("\n📝 Next steps:")
            for step in response["next_steps"]:
                print(f"  - {step}")

            print("\n📄 Files to generate:")
            for filename in response["files_to_create"].keys():
                print(f"  - {filename}")
        else:
            print("  ❌ Not detected as AI environment request")

        print("-" * 60)


def demo_model_info():
    """Show available models and their info"""
    print("\n" + "=" * 60)
    print("📚 Available AI/ML Models")
    print("=" * 60)

    architect = AIEnvironmentArchitect()

    print("\n✅ Stable (Pure Nix) Models:")
    for model, info in architect.model_requirements["stable"].items():
        print(f"\n  {model}:")
        print(f"    Description: {info['description']}")
        print(f"    CUDA: {'Required' if info['cuda'] else 'Not needed'}")
        print(f"    Min RAM: {info['min_ram']}")

    print("\n🔬 Experimental (Nix + pip) Models:")
    for model, info in architect.model_requirements["experimental"].items():
        print(f"\n  {model}:")
        print(f"    Description: {info['description']}")
        print(f"    CUDA: {'Required' if info['cuda'] else 'Not needed'}")
        print(f"    Min RAM: {info['min_ram']}")
        if "license_warning" in info:
            print(f"    ⚠️  License: {info['license_warning']}")


def main():
    """Run all demos"""
    print("🤖 AI Environment Architect Demo Suite")
    print("Natural language to Nix flake generation for AI/ML")
    print()

    # Run demos
    demo_basic_analysis()
    demo_flake_generation()
    demo_integration()
    demo_model_info()

    print("\n" + "=" * 60)
    print("✅ Demo complete!")
    print("\nTo use in production:")
    print("  ask-nix-ai-env 'your AI/ML environment request'")
    print("\nOr integrate with ask-nix for seamless experience!")
    print("=" * 60)


if __name__ == "__main__":
    main()
