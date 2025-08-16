#!/usr/bin/env python3
"""
Demo: Causal XAI for Package Installation

This demonstrates how the Causal XAI engine will explain
why it recommends installing a specific package.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib.pyplot as plt
import networkx as nx
from nix_humanity.xai import (
    CausalKnowledgeBase,
    CausalModelBuilder,
    Decision,
)
from nix_humanity.xai.models import CausalFactor


def visualize_causal_graph(kb: CausalKnowledgeBase, operation: str):
    """Visualize the causal graph for an operation"""
    model_dict = kb.get_model(operation)
    if not model_dict:
        print(f"No model found for {operation}")
        return

    # Build the graph
    graph = kb.build_graph(model_dict)

    # Create layout
    pos = nx.spring_layout(graph, k=3, iterations=50)

    # Color nodes by type
    node_colors = []
    for node in graph.nodes():
        node_type = graph.nodes[node].get("node_type", "unknown")
        if node_type == "treatment":
            node_colors.append("lightgreen")
        elif node_type == "outcome":
            node_colors.append("lightcoral")
        elif node_type == "confounder":
            node_colors.append("lightyellow")
        else:
            node_colors.append("lightblue")

    # Draw the graph
    plt.figure(figsize=(12, 8))
    nx.draw(
        graph,
        pos,
        node_color=node_colors,
        node_size=2000,
        font_size=8,
        font_weight="bold",
        with_labels=True,
        arrows=True,
        arrowsize=20,
        edge_color="gray",
        linewidths=2,
    )

    # Add edge labels with strength
    edge_labels = {}
    for edge in graph.edges():
        strength = graph[edge[0]][edge[1]].get("strength", 0)
        edge_labels[edge] = f"{strength:.1f}"
    nx.draw_networkx_edge_labels(graph, pos, edge_labels, font_size=8)

    # Add title and legend
    plt.title(f"Causal Model: {operation.replace('_', ' ').title()}", fontsize=16)

    # Create legend
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor="lightgreen", label="Treatment"),
        Patch(facecolor="lightcoral", label="Outcome"),
        Patch(facecolor="lightyellow", label="Confounder"),
        Patch(facecolor="lightblue", label="Observed"),
    ]
    plt.legend(handles=legend_elements, loc="upper left")

    plt.tight_layout()
    plt.savefig(f"causal_model_{operation}.png", dpi=150, bbox_inches="tight")
    print(f"✅ Saved visualization to causal_model_{operation}.png")
    plt.close()


def demo_install_decision():
    """Demonstrate causal model for package installation"""
    print("=== Causal XAI Demo: Package Installation ===\n")

    # Initialize knowledge base and builder
    kb = CausalKnowledgeBase()
    builder = CausalModelBuilder(kb)

    # Create a decision to install Firefox
    decision = Decision(
        action="install",
        target="firefox",
        context={
            "user_need": "web_browser",
            "package_availability": True,
            "system_compatibility": True,
            "disk_space": True,
            "user_preference": "open_source",
            "user_level": "beginner",
            "alternatives_considered": ["chromium", "brave"],
        },
        confidence=0.92,
        alternatives=[
            {"package": "chromium", "score": 0.85},
            {"package": "brave", "score": 0.78},
        ],
        user_input="I need a web browser",
    )

    print(f"Decision: {decision.action} {decision.target}")
    print(f"User input: '{decision.user_input}'")
    print(f"Confidence: {decision.confidence:.0%}\n")

    # Build causal model
    print("Building causal model...")
    try:
        model = builder.build_model(decision)
        print("✅ Causal model built successfully")

        # Show model structure
        print("\n" + builder.visualize_model(model))

    except Exception as e:
        print(f"❌ Failed to build model: {e}")
        return

    # Simulate explanation generation
    print("\n=== Generated Explanations ===\n")

    # Simple explanation
    print("SIMPLE LEVEL:")
    print("I recommend installing Firefox because it best matches your need for an ")
    print("open-source web browser with high confidence.\n")

    # Detailed explanation
    print("DETAILED LEVEL:")
    print("I recommend install firefox based on several factors:")
    print(
        "• User need match: You asked for a web browser and Firefox perfectly matches this need"
    )
    print("• Package availability: Firefox is readily available in nixpkgs")
    print("• System compatibility: Your system meets all requirements")
    print(
        "• User preference: You prefer open-source software, and Firefox is fully open-source"
    )
    print("")
    print("My confidence in this recommendation is 92% based on causal analysis.")
    print("I also considered chromium (85% match) and brave (78% match) but found")
    print("Firefox most suitable for your needs.\n")

    # Expert explanation (simulated)
    print("EXPERT LEVEL:")
    print("Causal Factors (sorted by influence):")

    factors = [
        CausalFactor(
            "user_need_match",
            "web_browser",
            0.9,
            0.95,
            "Direct match for browser requirement",
        ),
        CausalFactor(
            "open_source_preference",
            True,
            0.8,
            0.90,
            "Firefox aligns with open-source preference",
        ),
        CausalFactor(
            "package_availability", True, 0.7, 1.0, "Package exists in nixpkgs"
        ),
        CausalFactor(
            "system_compatibility", True, 0.6, 0.95, "System meets all requirements"
        ),
        CausalFactor("community_support", "strong", 0.5, 0.85, "Large user community"),
    ]

    for factor in factors:
        print(f"  • {factor.name}: {factor.value}")
        print(
            f"    Influence: {factor.influence:+.1f}, Confidence: {factor.confidence:.0%}"
        )
        print(f"    {factor.description}")

    print("\nAlternatives rejected:")
    print("  • chromium: Lower open-source alignment score (proprietary components)")
    print("  • brave: Lower community trust score (newer, crypto features)")

    print("\nInference methods used:")
    print("  • Propensity Score Matching")
    print("  • Linear Regression")
    print("  • Backdoor Adjustment")

    # Visualize the causal graph
    print("\n=== Visualizing Causal Model ===")
    visualize_causal_graph(kb, "install_package")


def demo_counterfactual():
    """Demonstrate counterfactual reasoning"""
    print("\n=== Counterfactual Analysis ===\n")

    print("What if the user had different preferences?\n")

    print("Scenario 1: User prefers proprietary software")
    print("  → Chromium confidence increases to 88%")
    print("  → Firefox confidence decreases to 82%")
    print("  → Recommendation might change to Chromium\n")

    print("Scenario 2: User has limited disk space")
    print("  → All browser confidences decrease by 10%")
    print("  → System suggests lightweight alternatives")
    print("  → Recommendation includes disk cleanup suggestion\n")

    print("Scenario 3: User is an advanced developer")
    print("  → Installation method changes to declarative")
    print("  → Additional dev tools suggested (extensions)")
    print("  → Explanation becomes more technical")


def main():
    """Run the demo"""
    demo_install_decision()
    demo_counterfactual()

    print("\n=== Demo Complete ===")
    print("\nThis demonstrates how the Causal XAI engine will:")
    print("1. Build causal models for decisions")
    print("2. Generate multi-level explanations")
    print("3. Show confidence and alternatives")
    print("4. Perform counterfactual reasoning")
    print("\nNext steps: Implement the inference engine and explanation generator!")


if __name__ == "__main__":
    main()
