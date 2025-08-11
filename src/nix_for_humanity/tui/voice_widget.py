"""
Voice Interface Widget for TUI

Provides visual feedback for voice interactions including:
- Waveform visualization
- Voice state indicators
- Transcription display
"""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static, Label, ProgressBar
from rich.text import Text
from rich.panel import Panel
import asyncio
import random
from typing import Optional, List
from enum import Enum


class VoiceState(Enum):
    """Voice interface states"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


class WaveformDisplay(Widget):
    """Animated waveform visualization for voice activity"""
    
    DEFAULT_CSS = """
    WaveformDisplay {
        height: 5;
        width: 100%;
        border: solid cyan;
        padding: 1;
    }
    """
    
    audio_level = reactive(0.0)
    is_active = reactive(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.waveform_chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        self.waveform_data = [0.0] * 50  # 50 samples wide
        self.animation_task = None
        
    def on_mount(self):
        """Start animation when mounted"""
        self.animation_task = asyncio.create_task(self.animate_waveform())
        
    async def animate_waveform(self):
        """Animate the waveform display"""
        while True:
            if self.is_active:
                # Generate wave pattern when active
                self.waveform_data.pop(0)
                if self.audio_level > 0.1:
                    # Active speech - bigger waves
                    new_val = random.uniform(0.3, 1.0) * self.audio_level
                else:
                    # Background noise - small ripples
                    new_val = random.uniform(0.0, 0.2)
                self.waveform_data.append(new_val)
            else:
                # Flatten when inactive
                self.waveform_data = [v * 0.9 for v in self.waveform_data]
                self.waveform_data.pop(0)
                self.waveform_data.append(0.0)
            
            self.refresh()
            await asyncio.sleep(0.05)  # 20 FPS
    
    def render(self) -> Text:
        """Render the waveform"""
        if not self.is_active:
            return Text("💤 Voice Inactive", style="dim cyan")
        
        # Convert waveform data to characters
        wave_str = ""
        for value in self.waveform_data:
            char_idx = min(int(value * len(self.waveform_chars)), len(self.waveform_chars) - 1)
            wave_str += self.waveform_chars[char_idx]
        
        color = "bright_cyan" if self.audio_level > 0.5 else "cyan"
        return Text(wave_str, style=color)
    
    def set_audio_level(self, level: float):
        """Update audio level (0.0 to 1.0)"""
        self.audio_level = max(0.0, min(1.0, level))
        self.is_active = level > 0.01
    
    def stop(self):
        """Stop the animation"""
        if self.animation_task:
            self.animation_task.cancel()


class VoiceStatusIndicator(Static):
    """Shows current voice interface state with icons"""
    
    DEFAULT_CSS = """
    VoiceStatusIndicator {
        height: 3;
        width: 100%;
        text-align: center;
        padding: 1;
    }
    """
    
    STATE_DISPLAYS = {
        VoiceState.IDLE: ("😴", "Ready", "dim white"),
        VoiceState.LISTENING: ("👂", "Listening...", "bright_green"),
        VoiceState.PROCESSING: ("🤔", "Processing...", "bright_yellow"),
        VoiceState.SPEAKING: ("🗣️", "Speaking...", "bright_blue"),
        VoiceState.ERROR: ("❌", "Error", "bright_red"),
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = VoiceState.IDLE
        
    def update_state(self, state: VoiceState):
        """Update the voice state"""
        self.state = state
        icon, text, color = self.STATE_DISPLAYS[state]
        self.update(Text(f"{icon} {text}", style=color))


class TranscriptionDisplay(Static):
    """Shows the transcribed text from voice input"""
    
    DEFAULT_CSS = """
    TranscriptionDisplay {
        height: 4;
        width: 100%;
        border: solid green;
        padding: 1;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history: List[str] = []
        self.update_display()
        
    def add_transcription(self, text: str, is_user: bool = True):
        """Add a new transcription to the display"""
        prefix = "👤 You: " if is_user else "🤖 Nix: "
        self.history.append(prefix + text)
        if len(self.history) > 3:  # Keep last 3 entries
            self.history.pop(0)
        self.update_display()
        
    def update_display(self):
        """Update the display with current transcriptions"""
        if not self.history:
            self.update(Text("💬 Say 'Hey Nix' to start...", style="dim"))
        else:
            display_text = "\n".join(self.history)
            self.update(Text(display_text))
    
    def clear(self):
        """Clear the transcription history"""
        self.history = []
        self.update_display()


class VoiceInterfaceWidget(Widget):
    """
    Complete voice interface widget for TUI integration.
    
    Combines waveform, status, and transcription displays.
    """
    
    DEFAULT_CSS = """
    VoiceInterfaceWidget {
        height: 16;
        width: 100%;
        border: double magenta;
        padding: 1;
    }
    
    .voice-title {
        text-align: center;
        text-style: bold;
        color: bright_magenta;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.waveform = WaveformDisplay()
        self.status = VoiceStatusIndicator()
        self.transcription = TranscriptionDisplay()
        self.voice_interface = None  # Will be set by parent
        
    def compose(self) -> ComposeResult:
        """Create the voice interface layout"""
        with Vertical():
            yield Label("🎤 Voice Interface", classes="voice-title")
            yield self.status
            yield self.waveform
            yield self.transcription
    
    def on_voice_state_change(self, state: VoiceState):
        """Handle voice state changes"""
        self.status.update_state(state)
        
        if state == VoiceState.LISTENING:
            self.waveform.is_active = True
        elif state in [VoiceState.IDLE, VoiceState.ERROR]:
            self.waveform.is_active = False
    
    def on_audio_level(self, level: float):
        """Update waveform with audio level"""
        self.waveform.set_audio_level(level)
    
    def on_transcription(self, text: str, is_user: bool = True):
        """Handle new transcription"""
        self.transcription.add_transcription(text, is_user)
    
    def start_listening(self):
        """Start voice listening mode"""
        self.on_voice_state_change(VoiceState.LISTENING)
        
    def stop_listening(self):
        """Stop voice listening mode"""
        self.on_voice_state_change(VoiceState.IDLE)
        self.waveform.is_active = False
    
    async def simulate_conversation(self):
        """Simulate a voice conversation for demo"""
        conversations = [
            ("Hey Nix, install Firefox", "I'll help you install Firefox. Adding to configuration..."),
            ("Hey Nix, update my system", "Starting system update. This may take a few minutes..."),
            ("Hey Nix, what's installed?", "You have 247 packages installed including vim, git, python...")
        ]
        
        for user_text, nix_response in conversations:
            # User speaks
            self.on_voice_state_change(VoiceState.LISTENING)
            await asyncio.sleep(0.5)
            
            # Simulate audio levels during speech
            for _ in range(20):
                level = random.uniform(0.3, 0.9)
                self.on_audio_level(level)
                await asyncio.sleep(0.05)
            
            self.on_transcription(user_text, is_user=True)
            
            # Processing
            self.on_voice_state_change(VoiceState.PROCESSING)
            await asyncio.sleep(1.0)
            
            # Nix responds
            self.on_voice_state_change(VoiceState.SPEAKING)
            self.on_transcription(nix_response, is_user=False)
            await asyncio.sleep(2.0)
            
            # Back to idle
            self.on_voice_state_change(VoiceState.IDLE)
            await asyncio.sleep(1.0)


class VoiceControlPanel(Widget):
    """Control panel for voice interface with buttons"""
    
    DEFAULT_CSS = """
    VoiceControlPanel {
        height: 5;
        width: 100%;
        layout: horizontal;
        align: center middle;
    }
    
    .voice-button {
        width: 20;
        height: 3;
        margin: 1;
        border: solid;
        text-align: center;
        padding: 1;
    }
    
    .voice-button:hover {
        background: $accent;
    }
    """
    
    def compose(self) -> ComposeResult:
        """Create control buttons"""
        with Horizontal():
            yield Static("[M]icrophone 🎤", classes="voice-button")
            yield Static("[T]est Voice 🔊", classes="voice-button")
            yield Static("[C]lear 🗑️", classes="voice-button")
            yield Static("[H]elp ❓", classes="voice-button")