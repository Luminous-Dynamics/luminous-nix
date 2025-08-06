"""
Accessible Widget Components for Nix for Humanity TUI
These widgets integrate with our screen reader support and accessibility framework
"""

from typing import Optional, Callable, Any
from textual.widgets import Button, Input, ListView, ProgressBar, Static
from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual import events

from ..accessibility import (
    ScreenReaderSupport,
    AriaLivePriority,
    PersonaAccessibilityAdapter,
    PersonaType
)


class AccessibleWidget:
    """Base mixin for accessible widgets"""
    
    def __init__(self, *args, **kwargs):
        # Extract accessibility options
        self.aria_label = kwargs.pop('aria_label', None)
        self.aria_description = kwargs.pop('aria_description', None)
        self.screen_reader = kwargs.pop('screen_reader', None)
        self.persona_adapter = kwargs.pop('persona_adapter', None)
        
        super().__init__(*args, **kwargs)
        
        # Set up screen reader support if not provided
        if self.screen_reader is None:
            self.screen_reader = ScreenReaderSupport()
            
        # Set up persona adapter if not provided
        if self.persona_adapter is None:
            self.persona_adapter = PersonaAccessibilityAdapter()
    
    def announce_to_screen_reader(self, text: str, priority: AriaLivePriority = AriaLivePriority.POLITE):
        """Announce text to screen reader"""
        if self.screen_reader:
            self.screen_reader.announce(text, priority)
    
    def on_focus(self) -> None:
        """Called when widget receives focus"""
        super().on_focus()
        
        # Announce widget to screen reader
        if self.aria_label:
            announcement = self.aria_label
            if self.aria_description:
                announcement += f", {self.aria_description}"
            self.announce_to_screen_reader(announcement, AriaLivePriority.ASSERTIVE)
    
    def get_accessibility_label(self) -> str:
        """Get the full accessibility label for this widget"""
        label = self.aria_label or str(self)
        if self.aria_description:
            label += f", {self.aria_description}"
        return label


class AccessibleButton(AccessibleWidget, Button):
    """Button with screen reader support"""
    
    def __init__(
        self, 
        label: str,
        *,
        variant: str = "primary",
        aria_label: Optional[str] = None,
        aria_description: Optional[str] = None,
        **kwargs
    ):
        # Default aria label to button text if not provided
        if aria_label is None:
            aria_label = f"Button: {label}"
            
        super().__init__(
            label,
            variant=variant,
            aria_label=aria_label,
            aria_description=aria_description,
            **kwargs
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press with screen reader feedback"""
        self.announce_to_screen_reader(f"{self.label} activated", AriaLivePriority.ASSERTIVE)
        # Let parent handle the actual press event
        super().on_button_pressed(event)


class AccessibleInput(AccessibleWidget, Input):
    """Input field with screen reader support"""
    
    def __init__(
        self,
        *,
        placeholder: str = "",
        aria_label: Optional[str] = None,
        aria_description: Optional[str] = None,
        **kwargs
    ):
        if aria_label is None:
            aria_label = f"Text input: {placeholder}" if placeholder else "Text input"
            
        super().__init__(
            placeholder=placeholder,
            aria_label=aria_label,
            aria_description=aria_description,
            **kwargs
        )
        
        # Track previous value for change announcements
        self._previous_value = ""
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Announce input changes to screen reader"""
        # Only announce if value actually changed
        if event.value != self._previous_value:
            # For single character changes, announce the character
            if len(event.value) == len(self._previous_value) + 1:
                new_char = event.value[-1]
                self.announce_to_screen_reader(f"Typed {new_char}", AriaLivePriority.OFF)
            elif len(event.value) == len(self._previous_value) - 1:
                self.announce_to_screen_reader("Character deleted", AriaLivePriority.OFF)
            else:
                # For larger changes, announce the full value
                self.announce_to_screen_reader(f"Input value: {event.value}", AriaLivePriority.POLITE)
                
            self._previous_value = event.value
            
        super().on_input_changed(event)
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Announce when input is submitted"""
        self.announce_to_screen_reader(f"Submitted: {event.value}", AriaLivePriority.ASSERTIVE)
        super().on_input_submitted(event)


class AccessibleList(AccessibleWidget, ListView):
    """List view with screen reader support"""
    
    def __init__(
        self,
        *children,
        aria_label: Optional[str] = None,
        aria_description: Optional[str] = None,
        **kwargs
    ):
        if aria_label is None:
            aria_label = "List"
            
        super().__init__(
            *children,
            aria_label=aria_label,
            aria_description=aria_description,
            **kwargs
        )
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Announce list selection to screen reader"""
        if event.item:
            # Try to get text representation of the selected item
            item_text = str(event.item)
            self.announce_to_screen_reader(
                f"Selected: {item_text}", 
                AriaLivePriority.ASSERTIVE
            )
        super().on_list_view_selected(event)
    
    def on_key(self, event: events.Key) -> None:
        """Handle keyboard navigation with announcements"""
        if event.key in ["up", "down", "home", "end", "pageup", "pagedown"]:
            # Let the list handle the navigation first
            super().on_key(event)
            
            # Then announce the new position
            if self.highlighted is not None:
                item_text = str(self.highlighted)
                position = self.index + 1
                total = len(self.children)
                self.announce_to_screen_reader(
                    f"{item_text}, item {position} of {total}",
                    AriaLivePriority.POLITE
                )
        else:
            super().on_key(event)


class AccessibleProgressBar(AccessibleWidget, ProgressBar):
    """Progress bar with screen reader announcements"""
    
    def __init__(
        self,
        *,
        total: float = 100,
        aria_label: Optional[str] = None,
        aria_description: Optional[str] = None,
        **kwargs
    ):
        if aria_label is None:
            aria_label = "Progress"
            
        super().__init__(
            total=total,
            aria_label=aria_label,
            aria_description=aria_description,
            **kwargs
        )
        
        # Track last announced percentage to avoid spam
        self._last_announced_percent = -1
    
    def update(self, *, progress: Optional[float] = None, total: Optional[float] = None) -> None:
        """Update progress with screen reader announcements"""
        super().update(progress=progress, total=total)
        
        # Calculate percentage
        if self.total > 0:
            percent = int((self.progress / self.total) * 100)
            
            # Only announce at 0%, 25%, 50%, 75%, and 100%
            announce_points = [0, 25, 50, 75, 100]
            
            for point in announce_points:
                if percent >= point and self._last_announced_percent < point:
                    if point == 0:
                        self.announce_to_screen_reader(
                            f"{self.aria_label} started",
                            AriaLivePriority.POLITE
                        )
                    elif point == 100:
                        self.announce_to_screen_reader(
                            f"{self.aria_label} complete",
                            AriaLivePriority.POLITE
                        )
                    else:
                        self.announce_to_screen_reader(
                            f"{self.aria_label} {point}%",
                            AriaLivePriority.POLITE
                        )
                    self._last_announced_percent = percent
                    break


class AccessibleNotification(AccessibleWidget, Static):
    """Notification widget with automatic screen reader announcements"""
    
    def __init__(
        self,
        message: str,
        *,
        severity: str = "info",  # info, success, warning, error
        aria_label: Optional[str] = None,
        aria_description: Optional[str] = None,
        auto_dismiss: bool = True,
        dismiss_after: float = 5.0,
        **kwargs
    ):
        # Set aria label based on severity
        if aria_label is None:
            severity_labels = {
                "info": "Information",
                "success": "Success",
                "warning": "Warning",
                "error": "Error"
            }
            aria_label = f"{severity_labels.get(severity, 'Notification')}: {message}"
            
        super().__init__(
            message,
            aria_label=aria_label,
            aria_description=aria_description,
            **kwargs
        )
        
        self.severity = severity
        self.auto_dismiss = auto_dismiss
        self.dismiss_after = dismiss_after
        
        # Add CSS classes for styling
        self.add_class(f"notification-{severity}")
    
    def on_mount(self) -> None:
        """Announce notification when mounted"""
        super().on_mount()
        
        # Determine priority based on severity
        priority = AriaLivePriority.POLITE
        if self.severity == "error":
            priority = AriaLivePriority.ASSERTIVE
        elif self.severity == "warning":
            priority = AriaLivePriority.ASSERTIVE
            
        # Announce the notification
        self.announce_to_screen_reader(self.aria_label, priority)
        
        # Set up auto-dismiss if enabled
        if self.auto_dismiss:
            self.set_timer(self.dismiss_after, self.remove)


def create_accessible_widget(
    widget_type: str,
    persona: Optional[PersonaType] = None,
    **kwargs
) -> AccessibleWidget:
    """
    Factory function to create accessible widgets configured for specific personas
    
    Args:
        widget_type: Type of widget to create ('button', 'input', 'list', 'progress', 'notification')
        persona: Optional persona to configure accessibility settings for
        **kwargs: Additional arguments passed to widget constructor
        
    Returns:
        Configured accessible widget
    """
    # Create persona adapter if persona specified
    persona_adapter = None
    if persona:
        persona_adapter = PersonaAccessibilityAdapter()
        persona_adapter.set_persona(persona)
        
        # Get accessibility profile
        profile = persona_adapter.get_current_profile()
        
        # Apply persona-specific settings
        if profile.large_text:
            kwargs.setdefault('classes', '').add('large-text')
        if profile.high_contrast:
            kwargs.setdefault('classes', '').add('high-contrast')
            
    # Add persona adapter to kwargs
    kwargs['persona_adapter'] = persona_adapter
    
    # Create appropriate widget
    widget_map = {
        'button': AccessibleButton,
        'input': AccessibleInput,
        'list': AccessibleList,
        'progress': AccessibleProgressBar,
        'notification': AccessibleNotification
    }
    
    widget_class = widget_map.get(widget_type)
    if not widget_class:
        raise ValueError(f"Unknown widget type: {widget_type}")
        
    return widget_class(**kwargs)