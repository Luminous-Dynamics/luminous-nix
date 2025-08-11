"""
Custom Widgets for Nix for Humanity TUI.

Specialized widgets for enhanced user experience.

Since: v1.0.0
"""

from datetime import datetime
from typing import Any

from textual.containers import ScrollableContainer
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Input, Static


class CommandInput(Input):
    """
    Enhanced command input with autocomplete.

    Since: v1.0.0
    """

    class Submitted(Message):
        """Command submitted message."""

        def __init__(self, value: str):
            self.value = value
            super().__init__()

    def __init__(self, **kwargs):
        """Initialize command input."""
        super().__init__(**kwargs)
        self.suggestions: list[str] = []

    async def on_key(self, event) -> None:
        """Handle key events for autocomplete."""
        if event.key == "enter":
            self.post_message(self.Submitted(self.value))
        elif event.key == "tab" and self.suggestions:
            # Autocomplete with first suggestion
            if self.suggestions:
                self.value = self.suggestions[0]


class ResultsPanel(ScrollableContainer):
    """
    Panel for displaying command results.

    Since: v1.0.0
    """

    def __init__(self, **kwargs):
        """Initialize results panel."""
        super().__init__(**kwargs)
        self.results: list[dict[str, Any]] = []

    def add_result(self, result: dict[str, Any]) -> None:
        """Add a result to the panel."""
        self.results.append(result)

        # Create result widget
        success_emoji = "✅" if result.get("success") else "❌"

        result_text = f"""
{success_emoji} **Query:** {result.get('query', 'Unknown')}
**Time:** {result.get('timestamp', 'Unknown')}

{result.get('output', 'No output')}
        """

        # Add to container
        result_widget = Static(result_text, classes="result-item")
        self.mount(result_widget)

        # Scroll to bottom
        self.scroll_end()

    def clear(self) -> None:
        """Clear all results."""
        self.results.clear()
        self.remove_children()


class HistoryPanel(ScrollableContainer):
    """
    Panel for command history.

    Since: v1.0.0
    """

    def __init__(self, **kwargs):
        """Initialize history panel."""
        super().__init__(**kwargs)
        self.history: list[dict[str, Any]] = []

    def update_history(self, history: list[dict[str, Any]]) -> None:
        """Update history display."""
        self.history = history
        self.remove_children()

        for item in reversed(history):
            timestamp = item.get("timestamp", "")
            query = item.get("query", "")
            result = item.get("result", "")

            # Format timestamp
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime("%H:%M")
                except:
                    time_str = ""
            else:
                time_str = ""

            # Create history item
            emoji = "✅" if result == "success" else "❌"
            item_text = f"{time_str} {emoji} {query}"

            item_widget = Static(item_text, classes="history-item")
            self.mount(item_widget)


class StatusBar(Static):
    """
    Status bar showing current state.

    Since: v1.0.0
    """

    status_text = reactive("Ready")

    def __init__(self, **kwargs):
        """Initialize status bar."""
        super().__init__(**kwargs)

    def update_status(self, message: str) -> None:
        """Update status message."""
        self.status_text = message
        self.update(f" 📊 {message}")


class HelpPanel(ScrollableContainer):
    """
    Help panel with documentation.

    Since: v1.0.0
    """

    HELP_TEXT = """
# 🌟 Nix for Humanity - Help

## Natural Language Commands

Just type what you want to do:
- "install firefox" - Install a package
- "search editor" - Find packages
- "update system" - System update
- "remove vim" - Uninstall package
- "rollback" - Rollback to previous generation

## Keyboard Shortcuts

- **Ctrl+/** - Show this help
- **Ctrl+C** - Quit application
- **Ctrl+L** - Clear results
- **Ctrl+H** - Toggle history
- **Ctrl+P** - Toggle plugins
- **Ctrl+T** - Toggle theme
- **Tab** - Autocomplete / Next field
- **Enter** - Execute command

## Tips

- Use abbreviations: "i" for install, "s" for search
- Commands are safe by default (preview mode)
- History is saved automatically
- Plugins extend functionality

## Examples

1. **Install Development Tools**
   ```
   install python nodejs git
   ```

2. **Search for Editors**
   ```
   search code editor
   ```

3. **Update Everything**
   ```
   update system and all packages
   ```

4. **Generate Configuration**
   ```
   generate web server config
   ```
    """

    def __init__(self, **kwargs):
        """Initialize help panel."""
        super().__init__(**kwargs)
        help_widget = Static(self.HELP_TEXT)
        self.mount(help_widget)


class SearchResults(ScrollableContainer):
    """
    Live search results widget.

    Since: v1.0.0
    """

    def __init__(self, **kwargs):
        """Initialize search results."""
        super().__init__(**kwargs)
        self.results: list[dict[str, Any]] = []

    def update_results(self, results: list[dict[str, Any]]) -> None:
        """Update search results."""
        self.results = results
        self.remove_children()

        if not results:
            self.mount(Static("No results found", classes="info"))
            return

        # Display results
        for result in results:
            name = result.get("name", "Unknown")
            version = result.get("version", "")
            description = result.get("description", "")

            result_text = f"""
**{name}** {version}
{description}
            """

            result_widget = Static(result_text.strip(), classes="search-result")
            self.mount(result_widget)
