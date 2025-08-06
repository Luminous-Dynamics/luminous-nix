"""
Screen Reader Support Components
Provides utilities for making the TUI fully accessible to screen readers
"""

from typing import Optional, List, Dict, Callable, Any
from dataclasses import dataclass
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class AriaLivePriority(Enum):
    """ARIA live region priorities"""
    OFF = "off"
    POLITE = "polite"
    ASSERTIVE = "assertive"


@dataclass
class ScreenReaderAnnouncement:
    """Represents an announcement for screen readers"""
    text: str
    priority: AriaLivePriority = AriaLivePriority.POLITE
    clear_after: Optional[float] = None  # Clear after N seconds
    
    def __str__(self) -> str:
        """Text representation for screen readers"""
        return self.text


class AriaLiveRegion:
    """
    Manages ARIA live regions for dynamic content updates
    """
    
    def __init__(self, priority: AriaLivePriority = AriaLivePriority.POLITE):
        self.priority = priority
        self.announcements: List[ScreenReaderAnnouncement] = []
        self._listeners: List[Callable[[str, AriaLivePriority], None]] = []
        
    def announce(self, text: str, priority: Optional[AriaLivePriority] = None):
        """
        Make an announcement to screen readers
        
        Args:
            text: The text to announce
            priority: Override the default priority for this announcement
        """
        announcement_priority = priority or self.priority
        announcement = ScreenReaderAnnouncement(text, announcement_priority)
        
        self.announcements.append(announcement)
        
        # Notify listeners
        for listener in self._listeners:
            listener(text, announcement_priority)
            
        logger.debug(f"Screen reader announcement ({announcement_priority.value}): {text}")
        
    def add_listener(self, listener: Callable[[str, AriaLivePriority], None]):
        """Add a listener for announcements"""
        self._listeners.append(listener)
        
    def remove_listener(self, listener: Callable[[str, AriaLivePriority], None]):
        """Remove a listener"""
        if listener in self._listeners:
            self._listeners.remove(listener)
            
    def get_recent_announcements(self, count: int = 10) -> List[ScreenReaderAnnouncement]:
        """Get the most recent announcements"""
        return self.announcements[-count:]


class FocusManager:
    """
    Manages focus for keyboard navigation and screen readers
    """
    
    def __init__(self):
        self.focusable_elements: Dict[str, Dict[str, Any]] = {}
        self.focus_order: List[str] = []
        self.current_focus: Optional[str] = None
        self._focus_listeners: List[Callable[[str, str], None]] = []
        
    def register_focusable(
        self, 
        element_id: str, 
        label: str,
        description: Optional[str] = None,
        role: Optional[str] = None,
        shortcuts: Optional[Dict[str, str]] = None
    ):
        """
        Register a focusable element
        
        Args:
            element_id: Unique identifier for the element
            label: Accessible label for screen readers
            description: Extended description
            role: ARIA role (button, textbox, etc.)
            shortcuts: Keyboard shortcuts for this element
        """
        self.focusable_elements[element_id] = {
            'label': label,
            'description': description,
            'role': role,
            'shortcuts': shortcuts or {}
        }
        
        if element_id not in self.focus_order:
            self.focus_order.append(element_id)
            
    def set_focus(self, element_id: str):
        """Set focus to a specific element"""
        if element_id not in self.focusable_elements:
            logger.warning(f"Attempted to focus non-existent element: {element_id}")
            return
            
        old_focus = self.current_focus
        self.current_focus = element_id
        
        # Get element info for screen reader
        element = self.focusable_elements[element_id]
        announcement = f"{element['label']}"
        
        if element['role']:
            announcement = f"{element['role']}, {announcement}"
            
        if element['description']:
            announcement += f", {element['description']}"
            
        # Notify listeners
        for listener in self._focus_listeners:
            listener(element_id, announcement)
            
        logger.debug(f"Focus changed: {old_focus} → {element_id}")
        
    def focus_next(self):
        """Move focus to the next element"""
        if not self.focus_order:
            return
            
        if self.current_focus is None:
            self.set_focus(self.focus_order[0])
        else:
            try:
                current_index = self.focus_order.index(self.current_focus)
                next_index = (current_index + 1) % len(self.focus_order)
                self.set_focus(self.focus_order[next_index])
            except ValueError:
                self.set_focus(self.focus_order[0])
                
    def focus_previous(self):
        """Move focus to the previous element"""
        if not self.focus_order:
            return
            
        if self.current_focus is None:
            self.set_focus(self.focus_order[-1])
        else:
            try:
                current_index = self.focus_order.index(self.current_focus)
                prev_index = (current_index - 1) % len(self.focus_order)
                self.set_focus(self.focus_order[prev_index])
            except ValueError:
                self.set_focus(self.focus_order[-1])
                
    def add_focus_listener(self, listener: Callable[[str, str], None]):
        """Add a listener for focus changes"""
        self._focus_listeners.append(listener)
        
    def get_current_element_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently focused element"""
        if self.current_focus:
            return self.focusable_elements.get(self.current_focus)
        return None


class KeyboardNavigator:
    """
    Handles keyboard navigation for accessibility
    """
    
    def __init__(self, focus_manager: FocusManager):
        self.focus_manager = focus_manager
        self.shortcuts: Dict[str, Callable[[], None]] = {}
        self.skip_links: Dict[str, str] = {}
        
        # Register default navigation keys
        self.register_shortcut('tab', self.focus_manager.focus_next)
        self.register_shortcut('shift+tab', self.focus_manager.focus_previous)
        
    def register_shortcut(self, key_combo: str, action: Callable[[], None]):
        """Register a keyboard shortcut"""
        self.shortcuts[key_combo.lower()] = action
        logger.debug(f"Registered keyboard shortcut: {key_combo}")
        
    def register_skip_link(self, key: str, target_element_id: str, description: str):
        """
        Register a skip link for quick navigation
        
        Args:
            key: Keyboard key (e.g., '1', '2', etc.)
            target_element_id: Element to jump to
            description: Description of the skip target
        """
        self.skip_links[key] = target_element_id
        self.register_shortcut(
            key, 
            lambda: self._skip_to(target_element_id, description)
        )
        
    def _skip_to(self, element_id: str, description: str):
        """Skip to a specific element"""
        self.focus_manager.set_focus(element_id)
        # Announce the skip
        logger.info(f"Skipped to {description}")
        
    def handle_key(self, key_combo: str) -> bool:
        """
        Handle a keyboard input
        
        Returns:
            True if the key was handled, False otherwise
        """
        key_lower = key_combo.lower()
        
        if key_lower in self.shortcuts:
            self.shortcuts[key_lower]()
            return True
            
        return False
        
    def get_shortcuts_help(self) -> str:
        """Get a help string describing available shortcuts"""
        help_lines = ["Keyboard Navigation:"]
        
        # Basic navigation
        help_lines.append("  Tab - Next element")
        help_lines.append("  Shift+Tab - Previous element")
        
        # Skip links
        if self.skip_links:
            help_lines.append("\nQuick Navigation:")
            for key, element_id in self.skip_links.items():
                element = self.focus_manager.focusable_elements.get(element_id, {})
                label = element.get('label', element_id)
                help_lines.append(f"  {key} - Jump to {label}")
                
        # Other shortcuts
        other_shortcuts = {k: v for k, v in self.shortcuts.items() 
                          if k not in ['tab', 'shift+tab'] and k not in self.skip_links}
        if other_shortcuts:
            help_lines.append("\nOther Shortcuts:")
            for key in sorted(other_shortcuts.keys()):
                help_lines.append(f"  {key}")
                
        return "\n".join(help_lines)


class ScreenReaderSupport:
    """
    Main class for screen reader support integration
    """
    
    def __init__(self):
        self.aria_live = AriaLiveRegion()
        self.focus_manager = FocusManager()
        self.keyboard_nav = KeyboardNavigator(self.focus_manager)
        
        # Set up integration between components
        self.focus_manager.add_focus_listener(self._on_focus_change)
        
    def _on_focus_change(self, element_id: str, announcement: str):
        """Handle focus changes"""
        # Announce focus changes to screen readers
        self.aria_live.announce(announcement, AriaLivePriority.ASSERTIVE)
        
    def announce(self, text: str, priority: AriaLivePriority = AriaLivePriority.POLITE):
        """Make an announcement to screen readers"""
        self.aria_live.announce(text, priority)
        
    def announce_error(self, error_text: str):
        """Announce an error with high priority"""
        self.aria_live.announce(f"Error: {error_text}", AriaLivePriority.ASSERTIVE)
        
    def announce_success(self, success_text: str):
        """Announce a success message"""
        self.aria_live.announce(f"Success: {success_text}", AriaLivePriority.POLITE)
        
    def announce_progress(self, progress: int, task: str):
        """Announce progress updates"""
        if progress == 0:
            self.aria_live.announce(f"Starting {task}", AriaLivePriority.POLITE)
        elif progress == 100:
            self.aria_live.announce(f"Completed {task}", AriaLivePriority.POLITE)
        else:
            # Only announce at key intervals to avoid spam
            if progress in [25, 50, 75]:
                self.aria_live.announce(
                    f"Progress: {progress}% {task}", 
                    AriaLivePriority.POLITE
                )
                
    def create_semantic_structure(self) -> Dict[str, Dict[str, Any]]:
        """
        Create a semantic structure for screen readers
        Returns a dictionary describing the UI structure
        """
        return {
            'main': {
                'role': 'main',
                'label': 'Nix for Humanity Main Interface',
                'children': ['header', 'content', 'footer']
            },
            'header': {
                'role': 'banner',
                'label': 'Application Header',
                'contains': 'Nix for Humanity - Natural Language NixOS Interface'
            },
            'content': {
                'role': 'region',
                'label': 'Main Interaction Area',
                'aria-label': 'Command input and response display',
                'children': ['command_input', 'response_display', 'xai_panel']
            },
            'footer': {
                'role': 'contentinfo',
                'label': 'Application Footer',
                'contains': 'Keyboard shortcuts: Ctrl+H for help, Ctrl+X for explanations'
            }
        }