"""
TUI Integration for XAI explanations
Provides visual components for displaying causal explanations in Textual
"""

from typing import Optional, Dict, Any, List
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Static, Button, Label, ProgressBar, Tree
from textual.reactive import reactive
from textual import events
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree as RichTree
from rich.progress import Progress, SpinnerColumn, TextColumn
import asyncio

from .causal_engine import (
    CausalXAI,
    CausalExplanation,
    ExplanationLevel,
    ConfidenceLevel,
    DecisionNode
)
from .explanation_formatter import (
    ExplanationFormatter,
    PersonaType,
    PersonaExplanationAdapter
)
from .confidence_calculator import (
    ConfidenceCalculator,
    ConfidenceMetrics
)


class ExplanationPanel(Container):
    """Panel for displaying XAI explanations in the TUI"""
    
    DEFAULT_CSS = """
    ExplanationPanel {
        height: auto;
        border: solid $primary;
        background: $panel;
        padding: 1;
        margin: 1;
    }
    
    ExplanationPanel.low-confidence {
        border: solid $warning;
    }
    
    ExplanationPanel.high-confidence {
        border: solid $success;
    }
    
    .explanation-title {
        text-style: bold;
        color: $text;
        margin-bottom: 1;
    }
    
    .confidence-indicator {
        width: 100%;
        height: 1;
        margin: 1 0;
    }
    
    .factor-list {
        margin-left: 2;
    }
    
    .alternative-section {
        margin-top: 1;
        border-top: dashed $surface;
        padding-top: 1;
    }
    """
    
    def __init__(
        self,
        explanation: Optional[CausalExplanation] = None,
        persona: Optional[PersonaType] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.explanation = explanation
        self.persona = persona or PersonaType.GRANDMA_ROSE
        self.formatter = ExplanationFormatter()
        self.expanded = False
    
    def compose(self) -> ComposeResult:
        """Compose the explanation panel"""
        if not self.explanation:
            yield Static("No explanation available", classes="explanation-empty")
            return
        
        # Format for persona
        formatted = self.formatter.persona_adapter.adapt_for_persona(
            self.explanation,
            self.persona
        )
        
        # Title
        yield Static(
            f"🤔 Why I made this decision",
            classes="explanation-title"
        )
        
        # Main explanation
        yield Static(formatted["text"])
        
        # Confidence indicator
        confidence_pct = self.explanation.confidence_score * 100
        yield ProgressBar(
            total=100,
            show_eta=False,
            show_percentage=True,
            classes="confidence-indicator"
        )
        yield Static(f"Confidence: {formatted['confidence']}")
        
        # Details (if persona wants them)
        if self.expanded and "details" in formatted:
            yield Static("Contributing factors:", classes="factor-title")
            factor_list = Vertical(classes="factor-list")
            for factor in formatted["details"]:
                factor_list.compose_add_child(
                    Static(f"• {factor}")
                )
            yield factor_list
        
        # Alternatives (if available)
        if self.expanded and "alternatives" in formatted:
            alt_section = Vertical(classes="alternative-section")
            alt_section.compose_add_child(
                Static("Alternative approaches:", classes="alt-title")
            )
            for alt in formatted["alternatives"]:
                alt_section.compose_add_child(
                    Static(f"• {alt['option']}: {alt['reason']}")
                )
            yield alt_section
        
        # Expand/collapse button
        if self.persona not in [PersonaType.MAYA_ADHD, PersonaType.GRANDMA_ROSE]:
            yield Button(
                "Show more" if not self.expanded else "Show less",
                id="expand-explanation"
            )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle expand/collapse button"""
        if event.button.id == "expand-explanation":
            self.expanded = not self.expanded
            self.refresh()
    
    def update_explanation(
        self,
        explanation: CausalExplanation,
        persona: Optional[PersonaType] = None
    ) -> None:
        """Update with new explanation"""
        self.explanation = explanation
        if persona:
            self.persona = persona
        
        # Update CSS class based on confidence
        self.remove_class("low-confidence", "high-confidence")
        if explanation.confidence == ConfidenceLevel.LOW:
            self.add_class("low-confidence")
        elif explanation.confidence in [ConfidenceLevel.HIGH, ConfidenceLevel.CERTAIN]:
            self.add_class("high-confidence")
        
        self.refresh()


class ConfidenceDetailsWidget(Container):
    """Detailed confidence breakdown widget"""
    
    DEFAULT_CSS = """
    ConfidenceDetailsWidget {
        height: auto;
        padding: 1;
        background: $surface;
        border: solid $primary-lighten-2;
    }
    
    .confidence-header {
        text-style: bold;
        margin-bottom: 1;
    }
    
    .confidence-component {
        margin: 0 0 1 2;
    }
    
    .uncertainty-list {
        color: $warning;
        margin-top: 1;
    }
    """
    
    def __init__(self, metrics: Optional[ConfidenceMetrics] = None, **kwargs):
        super().__init__(**kwargs)
        self.metrics = metrics
    
    def compose(self) -> ComposeResult:
        """Compose confidence details"""
        if not self.metrics:
            yield Static("No confidence metrics available")
            return
        
        yield Static(
            f"📊 Confidence Analysis ({self.metrics.overall_confidence:.1%})",
            classes="confidence-header"
        )
        
        # Component breakdown
        if self.metrics.components:
            table = Table(show_header=True, header_style="bold")
            table.add_column("Factor", style="cyan")
            table.add_column("Confidence", justify="right")
            table.add_column("Weight", justify="right")
            
            for comp in sorted(self.metrics.components, 
                             key=lambda c: c.weighted_value, 
                             reverse=True):
                table.add_row(
                    comp.description,
                    f"{comp.value:.1%}",
                    f"{comp.weight:.2f}"
                )
            
            yield Static(table)
        
        # Uncertainties
        if self.metrics.uncertainty_factors:
            yield Static("⚠️ Uncertainties:", classes="uncertainty-header")
            uncertainty_list = Vertical(classes="uncertainty-list")
            for uncertainty in self.metrics.uncertainty_factors:
                uncertainty_list.compose_add_child(
                    Static(f"• {uncertainty}")
                )
            yield uncertainty_list
        
        # Trend indicator
        trend_symbol = {
            "increasing": "📈",
            "stable": "➡️",
            "decreasing": "📉"
        }.get(self.metrics.confidence_trend, "❓")
        
        yield Static(
            f"Trend: {trend_symbol} {self.metrics.confidence_trend}"
        )


class DecisionTreeWidget(ScrollableContainer):
    """Interactive decision tree visualization"""
    
    DEFAULT_CSS = """
    DecisionTreeWidget {
        height: 20;
        border: solid $primary;
        background: $panel;
        padding: 1;
    }
    
    .tree-node {
        margin-left: 2;
    }
    
    .node-confident {
        color: $success;
    }
    
    .node-uncertain {
        color: $warning;
    }
    """
    
    def __init__(self, explanation: Optional[CausalExplanation] = None, **kwargs):
        super().__init__(**kwargs)
        self.explanation = explanation
    
    def compose(self) -> ComposeResult:
        """Compose decision tree"""
        if not self.explanation:
            yield Static("No decision tree available")
            return
        
        tree = RichTree("🌳 Decision Path")
        
        # Add decision node
        decision_node = tree.add(f"[bold]{self.explanation.decision}[/bold]")
        
        # Add contributing factors
        for factor in self.explanation.contributing_factors:
            style = "green" if factor.confidence > 0.8 else "yellow" if factor.confidence > 0.5 else "red"
            factor_node = decision_node.add(
                f"[{style}]{factor.description} ({factor.confidence:.0%})[/{style}]"
            )
            
            # Add evidence
            for evidence in factor.contributing_factors:
                factor_node.add(f"[dim]• {evidence}[/dim]")
        
        # Add alternatives
        if self.explanation.alternative_paths:
            alt_node = tree.add("[bold]Alternative Approaches[/bold]")
            for alt in self.explanation.alternative_paths:
                alt_node.add(
                    f"{alt['decision']} - {alt['reason']} "
                    f"[dim]({alt.get('confidence', 0):.0%})[/dim]"
                )
        
        yield Static(tree)


class XAIExplanationModal(Container):
    """Modal dialog for detailed XAI explanations"""
    
    DEFAULT_CSS = """
    XAIExplanationModal {
        align: center middle;
        background: $background 80%;
        padding: 2;
    }
    
    .modal-content {
        width: 80;
        height: 40;
        background: $panel;
        border: thick $primary;
        padding: 2;
    }
    
    .modal-header {
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }
    
    .modal-tabs {
        height: 3;
        margin-bottom: 1;
    }
    
    .tab-content {
        height: 30;
    }
    """
    
    def __init__(
        self,
        explanation: CausalExplanation,
        confidence_metrics: Optional[ConfidenceMetrics] = None,
        persona: Optional[PersonaType] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.explanation = explanation
        self.confidence_metrics = confidence_metrics
        self.persona = persona or PersonaType.GRANDMA_ROSE
        self.current_tab = "explanation"
    
    def compose(self) -> ComposeResult:
        """Compose modal content"""
        with Vertical(classes="modal-content"):
            # Header
            yield Static(
                "🧠 AI Decision Explanation",
                classes="modal-header"
            )
            
            # Tab buttons
            with Horizontal(classes="modal-tabs"):
                yield Button("Explanation", id="tab-explanation", variant="primary")
                yield Button("Confidence", id="tab-confidence")
                yield Button("Decision Tree", id="tab-tree")
                yield Button("Close", id="close-modal", variant="error")
            
            # Tab content
            with Container(classes="tab-content"):
                if self.current_tab == "explanation":
                    yield ExplanationPanel(
                        self.explanation,
                        self.persona
                    )
                elif self.current_tab == "confidence" and self.confidence_metrics:
                    yield ConfidenceDetailsWidget(self.confidence_metrics)
                elif self.current_tab == "tree":
                    yield DecisionTreeWidget(self.explanation)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle tab switching"""
        if event.button.id == "close-modal":
            self.remove()
        elif event.button.id.startswith("tab-"):
            self.current_tab = event.button.id.replace("tab-", "")
            self.refresh()


class XAIIntegration:
    """Integration helper for adding XAI to TUI applications"""
    
    def __init__(self):
        self.xai_engine = CausalXAI()
        self.confidence_calculator = ConfidenceCalculator()
        self.formatter = ExplanationFormatter()
    
    async def explain_decision_async(
        self,
        decision: str,
        context: Dict[str, Any],
        level: ExplanationLevel = ExplanationLevel.SIMPLE
    ) -> tuple[CausalExplanation, ConfidenceMetrics]:
        """Generate explanation asynchronously"""
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        
        explanation = await loop.run_in_executor(
            None,
            self.xai_engine.explain_decision,
            decision,
            context,
            level
        )
        
        confidence = await loop.run_in_executor(
            None,
            self.confidence_calculator.calculate_confidence,
            decision,
            context,
            True
        )
        
        return explanation, confidence
    
    def create_explanation_panel(
        self,
        explanation: CausalExplanation,
        persona: Optional[PersonaType] = None
    ) -> ExplanationPanel:
        """Create an explanation panel widget"""
        return ExplanationPanel(explanation, persona)
    
    def create_confidence_widget(
        self,
        metrics: ConfidenceMetrics
    ) -> ConfidenceDetailsWidget:
        """Create a confidence details widget"""
        return ConfidenceDetailsWidget(metrics)
    
    def create_modal(
        self,
        explanation: CausalExplanation,
        confidence: Optional[ConfidenceMetrics] = None,
        persona: Optional[PersonaType] = None
    ) -> XAIExplanationModal:
        """Create a modal dialog for detailed explanations"""
        return XAIExplanationModal(explanation, confidence, persona)
    
    def format_inline_explanation(
        self,
        explanation: CausalExplanation,
        persona: Optional[PersonaType] = None
    ) -> str:
        """Format explanation for inline display"""
        formatted = self.formatter.format_explanation(
            explanation,
            "text",
            persona
        )
        return formatted