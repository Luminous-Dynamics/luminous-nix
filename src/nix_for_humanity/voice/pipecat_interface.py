"""
🎤 Pipecat Voice Interface for Nix for Humanity

Real-time, low-latency conversational AI interface using the pipecat framework.
Enables natural voice conversations with the consciousness-first computing system.

Architecture:
- Real-time audio processing pipeline
- Persona-aware voice adaptation 
- Privacy-first local processing
- Accessibility-optimized design
- Natural conversation flow
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Callable, List
from pathlib import Path
import json
from datetime import datetime
import threading
import queue

# Pipecat framework imports (will be available when installed)
try:
    from pipecat.frames import AudioRawFrame, TextFrame, StartFrame, EndFrame
    from pipecat.pipeline import Pipeline, Source, Sink, Processor
    from pipecat.transports.local import LocalTransport
    from pipecat.services.whisper import WhisperSTTService
    from pipecat.services.piper import PiperTTSService
    from pipecat.processors.conversation import ConversationProcessor
    from pipecat.processors.vad import VADProcessor
    PIPECAT_AVAILABLE = True
except ImportError:
    # Mock classes for development when pipecat not installed
    PIPECAT_AVAILABLE = False
    class Pipeline: pass
    class Source: pass  
    class Processor: pass
    class AudioRawFrame: pass
    class TextFrame: pass
    class StartFrame: pass
    class EndFrame: pass

from .voice_config import VoiceConfig, PersonaVoiceSettings, EmotionTone
from ..interfaces.backend_interface import BackendInterface
from ..core.types import ConversationContext

logger = logging.getLogger(__name__)


class PipecatVoiceInterface:
    """
    Real-time voice interface using pipecat for natural conversation.
    
    This interface creates a complete conversational AI pipeline:
    Audio Input → Speech Recognition → NLP Processing → Response Generation → Speech Synthesis → Audio Output
    """
    
    def __init__(
        self,
        nix_interface: BackendInterface,
        voice_config: Optional[VoiceConfig] = None,
        data_dir: Optional[Path] = None
    ):
        self.nix_interface = nix_interface
        self.voice_config = voice_config or VoiceConfig()
        self.data_dir = data_dir or Path.home() / ".local/share/nix-humanity"
        
        # Pipeline components
        self.pipeline: Optional[Pipeline] = None
        self.transport: Optional[LocalTransport] = None
        self.stt_service = None
        self.tts_service = None
        self.conversation_processor = None
        
        # State management
        self.is_listening = False
        self.is_speaking = False
        self.current_conversation: Optional[ConversationContext] = None
        self.audio_queue = queue.Queue()
        
        # Statistics and learning
        self.interaction_stats = {
            "total_conversations": 0,
            "average_response_time": 0.0,
            "persona_adaptations": {},
            "successful_completions": 0,
        }
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize pipecat components
        if PIPECAT_AVAILABLE:
            self._initialize_pipeline()
        else:
            logger.warning("Pipecat not available. Voice interface will use mock implementation.")
    
    def _initialize_pipeline(self) -> None:
        """Initialize the pipecat processing pipeline."""
        try:
            persona = self.voice_config.get_persona_settings()
            
            # Initialize STT service (Speech to Text)
            if persona.stt_provider.value == "whisper-cpp":
                self.stt_service = WhisperSTTService(
                    model_path=self._get_whisper_model_path(),
                    language=persona.language,
                    sample_rate=self.voice_config.sample_rate,
                )
            else:
                # Fallback to mock implementation
                self.stt_service = MockSTTService()
            
            # Initialize TTS service (Text to Speech)  
            if persona.tts_provider.value == "piper":
                self.tts_service = PiperTTSService(
                    voice_path=self._get_piper_voice_path(persona),
                    sample_rate=self.voice_config.sample_rate,
                    speed=persona.voice_speed,
                )
            else:
                # Fallback to mock implementation
                self.tts_service = MockTTSService()
            
            # Initialize conversation processor
            self.conversation_processor = NixHumanityConversationProcessor(
                nix_interface=self.nix_interface,
                persona_settings=persona
            )
            
            # Initialize VAD (Voice Activity Detection)
            vad_processor = VADProcessor(
                threshold=0.5,
                silence_duration=persona.silence_timeout_ms / 1000.0
            )
            
            # Create the processing pipeline
            self.pipeline = Pipeline([
                vad_processor,
                self.stt_service,
                self.conversation_processor,
                self.tts_service,
            ])
            
            # Initialize transport (audio I/O)
            self.transport = LocalTransport(
                sample_rate=self.voice_config.sample_rate,
                channels=self.voice_config.channels,
                input_device=self.voice_config.audio_device_input,
                output_device=self.voice_config.audio_device_output,
            )
            
            logger.info(f"Pipecat pipeline initialized for persona: {persona.persona_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize pipecat pipeline: {e}")
            self._initialize_mock_pipeline()
    
    def _initialize_mock_pipeline(self) -> None:
        """Initialize mock pipeline for development/testing."""
        logger.info("Initializing mock voice pipeline for development")
        self.stt_service = MockSTTService()
        self.tts_service = MockTTSService()
        self.conversation_processor = MockConversationProcessor(self.nix_interface)
    
    async def start_listening(self, 
                            on_transcript: Optional[Callable[[str], None]] = None,
                            on_response: Optional[Callable[[str], None]] = None) -> None:
        """
        Start the voice interface and begin listening for user input.
        
        Args:
            on_transcript: Callback for when speech is transcribed
            on_response: Callback for when AI generates a response
        """
        if self.is_listening:
            logger.warning("Voice interface is already listening")
            return
        
        self.is_listening = True
        persona = self.voice_config.get_persona_settings()
        
        logger.info(f"🎤 Starting voice interface for {persona.persona_name}")
        logger.info(f"   - Max response time: {persona.max_response_time_ms}ms")
        logger.info(f"   - Silence timeout: {persona.silence_timeout_ms}ms")
        logger.info(f"   - Interruption allowed: {persona.interruption_allowed}")
        
        try:
            if PIPECAT_AVAILABLE and self.pipeline and self.transport:
                # Start the real pipecat pipeline
                await self._start_real_pipeline(on_transcript, on_response)
            else:
                # Start mock pipeline for development
                await self._start_mock_pipeline(on_transcript, on_response)
                
        except Exception as e:
            logger.error(f"Failed to start voice interface: {e}")
            self.is_listening = False
            raise
    
    async def _start_real_pipeline(self, on_transcript, on_response) -> None:
        """Start the real pipecat processing pipeline."""
        
        # Set up event handlers
        if on_transcript:
            self.conversation_processor.on_transcript = on_transcript
        if on_response:
            self.conversation_processor.on_response = on_response
        
        # Connect pipeline to transport
        await self.transport.connect(self.pipeline)
        
        # Start processing
        start_frame = StartFrame()
        await self.pipeline.process_frame(start_frame)
        
        # Begin audio capture and processing loop
        async def audio_loop():
            while self.is_listening:
                try:
                    # Get audio frame from transport
                    audio_frame = await self.transport.get_audio_frame()
                    if audio_frame:
                        await self.pipeline.process_frame(audio_frame)
                    
                    # Small delay to prevent CPU spinning
                    await asyncio.sleep(0.01)
                    
                except Exception as e:
                    logger.error(f"Error in audio processing loop: {e}")
                    break
        
        # Start the audio processing loop
        await audio_loop()
    
    async def _start_mock_pipeline(self, on_transcript, on_response) -> None:
        """Start mock pipeline for development/testing."""
        logger.info("🎭 Starting mock voice pipeline")
        
        # Simulate voice interaction
        async def mock_interaction():
            await asyncio.sleep(2)  # Simulate listening time
            
            # Simulate speech recognition
            mock_transcript = "install firefox please"
            logger.info(f"🎤 [MOCK] Transcript: {mock_transcript}")
            if on_transcript:
                on_transcript(mock_transcript)
            
            # Process through NixOS interface
            start_time = datetime.now()
            try:
                response = await self.nix_interface.process_natural_language(
                    mock_transcript,
                    context=ConversationContext(
                        persona=self.voice_config.active_persona,
                        interface_type="voice",
                        conversation_id=f"voice_{datetime.now().isoformat()}"
                    )
                )
                
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                # Check if response is within persona's acceptable time
                persona = self.voice_config.get_persona_settings()
                if response_time > persona.max_response_time_ms:
                    logger.warning(f"Response time {response_time:.0f}ms exceeds persona limit {persona.max_response_time_ms}ms")
                
                # Generate speech response
                speech_text = self._format_response_for_speech(response, persona)
                logger.info(f"🗣️ [MOCK] Response: {speech_text}")
                
                if on_response:
                    on_response(speech_text)
                
                # Simulate TTS duration  
                tts_duration = len(speech_text) * 50  # Mock: 50ms per character
                await asyncio.sleep(tts_duration / 1000.0)
                
                # Update statistics
                self._update_interaction_stats(response_time, True)
                
            except Exception as e:
                logger.error(f"Error processing voice command: {e}")
                error_response = self._generate_error_response(str(e), self.voice_config.get_persona_settings())
                if on_response:
                    on_response(error_response)
        
        # Start mock interaction
        asyncio.create_task(mock_interaction())
    
    async def stop_listening(self) -> None:
        """Stop the voice interface."""
        if not self.is_listening:
            return
        
        self.is_listening = False
        logger.info("🔇 Stopping voice interface")
        
        try:
            if PIPECAT_AVAILABLE and self.pipeline:
                # Send end frame to pipeline
                end_frame = EndFrame()
                await self.pipeline.process_frame(end_frame)
                
                # Disconnect transport
                if self.transport:
                    await self.transport.disconnect()
            
            # Save interaction statistics
            await self._save_interaction_stats()
            
        except Exception as e:
            logger.error(f"Error stopping voice interface: {e}")
    
    async def speak(self, text: str, emotion: Optional[EmotionTone] = None) -> None:
        """
        Synthesize speech for the given text.
        
        Args:
            text: Text to speak
            emotion: Emotional tone to use
        """
        if self.is_speaking:
            logger.warning("Already speaking, queueing message")
        
        self.is_speaking = True
        persona = self.voice_config.get_persona_settings()
        
        try:
            # Format text for the persona
            formatted_text = self._format_response_for_speech(text, persona)
            
            if PIPECAT_AVAILABLE and self.tts_service:
                # Use real TTS service
                text_frame = TextFrame(formatted_text)
                audio_frame = await self.tts_service.process_frame(text_frame)
                
                # Play through transport
                if self.transport and audio_frame:
                    await self.transport.send_audio_frame(audio_frame)
            else:
                # Mock TTS
                logger.info(f"🗣️ [MOCK] Speaking: {formatted_text}")
                # Simulate speaking duration
                duration = len(formatted_text) * persona.voice_speed * 0.05  # 50ms per char adjusted for speed
                await asyncio.sleep(duration)
            
        except Exception as e:
            logger.error(f"Error in speech synthesis: {e}")
        finally:
            self.is_speaking = False
    
    def set_persona(self, persona_name: str) -> bool:
        """
        Switch to a different persona configuration.
        
        Args:
            persona_name: Name of the persona to switch to
            
        Returns:
            True if persona was successfully set
        """
        if self.voice_config.set_active_persona(persona_name):
            logger.info(f"🎭 Switched to persona: {persona_name}")
            
            # Reinitialize pipeline with new persona settings if needed
            if PIPECAT_AVAILABLE:
                asyncio.create_task(self._reinitialize_for_persona())
            
            return True
        else:
            logger.error(f"Unknown persona: {persona_name}")
            return False
    
    async def _reinitialize_for_persona(self) -> None:
        """Reinitialize pipeline components for new persona."""
        try:
            was_listening = self.is_listening
            
            if was_listening:
                await self.stop_listening()
                
            # Reinitialize with new persona settings
            self._initialize_pipeline()
            
            if was_listening:
                await self.start_listening()
                
        except Exception as e:
            logger.error(f"Error reinitializing for persona: {e}")
    
    def _format_response_for_speech(self, response: Any, persona: PersonaVoiceSettings) -> str:
        """Format response text for speech synthesis based on persona."""
        if isinstance(response, str):
            text = response
        elif hasattr(response, 'display_text'):
            text = response.display_text
        elif hasattr(response, 'message'):
            text = response.message
        else:
            text = str(response)
        
        # Apply persona-specific formatting
        if not persona.technical_terms:
            # Replace technical terms with friendly language
            text = text.replace("nix-env", "package manager")
            text = text.replace("nixpkgs", "software collection")
            text = text.replace("derivation", "package")
            text = text.replace("configuration.nix", "system settings")
        
        # Add emotional context
        if persona.default_emotion == EmotionTone.ENCOURAGING:
            if "installing" in text.lower():
                text = f"Great choice! {text}"
            elif "error" in text.lower():
                text = f"No worries, let's fix this. {text}"
        elif persona.default_emotion == EmotionTone.PATIENT:
            if "..." in text:
                text = text.replace("...", ". Take your time.")
        
        # Adjust for accessibility needs
        if "clear_speech" in persona.accessibility_needs:
            # Add pauses for clarity
            text = text.replace(".", ". ").replace("!", "! ").replace("?", "? ")
            # Remove multiple spaces
            text = " ".join(text.split())
        
        return text.strip()
    
    def _generate_error_response(self, error: str, persona: PersonaVoiceSettings) -> str:
        """Generate persona-appropriate error response."""
        if persona.persona_name == "Grandma Rose":
            return "I'm sorry, I had a little trouble with that. Could you try asking again in a different way?"
        elif persona.persona_name == "Maya":
            return "Error. Try again?"
        elif persona.persona_name == "David":
            return "Sorry, that didn't work. Let me help you find another way."
        elif persona.persona_name == "Alex":
            return f"Error encountered: {error}. Alternative approaches available."
        else:
            return f"I encountered an issue: {error}. Would you like to try a different approach?"
    
    def _update_interaction_stats(self, response_time_ms: float, success: bool) -> None:
        """Update interaction statistics for learning and optimization."""
        stats = self.interaction_stats
        
        stats["total_conversations"] += 1
        
        # Update average response time
        current_avg = stats["average_response_time"]
        total = stats["total_conversations"]
        stats["average_response_time"] = ((current_avg * (total - 1)) + response_time_ms) / total
        
        if success:
            stats["successful_completions"] += 1
        
        # Track persona-specific stats
        persona_name = self.voice_config.active_persona
        if persona_name not in stats["persona_adaptations"]:
            stats["persona_adaptations"][persona_name] = {
                "interactions": 0,
                "avg_response_time": 0.0,
                "success_rate": 0.0
            }
        
        persona_stats = stats["persona_adaptations"][persona_name]
        persona_stats["interactions"] += 1
        
        # Update persona average response time
        p_total = persona_stats["interactions"]
        p_current_avg = persona_stats["avg_response_time"]
        persona_stats["avg_response_time"] = ((p_current_avg * (p_total - 1)) + response_time_ms) / p_total
        
        # Update persona success rate
        if success:
            persona_stats["success_rate"] = (persona_stats.get("successes", 0) + 1) / p_total
            persona_stats["successes"] = persona_stats.get("successes", 0) + 1
    
    async def _save_interaction_stats(self) -> None:
        """Save interaction statistics to disk."""
        try:
            stats_file = self.data_dir / "voice_interaction_stats.json"
            with open(stats_file, 'w') as f:
                json.dump({
                    **self.interaction_stats,
                    "last_updated": datetime.now().isoformat(),
                    "active_persona": self.voice_config.active_persona
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save interaction stats: {e}")
    
    def _get_whisper_model_path(self) -> Path:
        """Get path to Whisper model file using Model Manager."""
        try:
            # Import here to avoid circular dependencies
            from .model_manager import get_whisper_model_path, ModelSize
            
            # Use model manager to get appropriate model
            # This will download if not available
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                path = loop.run_until_complete(
                    get_whisper_model_path(self.data_dir, ModelSize.BASE)
                )
                return path
            finally:
                loop.close()
                
        except Exception as e:
            logger.warning(f"Model Manager failed, using fallback: {e}")
            # Fallback to original behavior
            models_dir = self.data_dir / "models" / "whisper"
            models_dir.mkdir(parents=True, exist_ok=True)
            return models_dir / "ggml-base.en.bin"  # Fallback model
    
    def _get_piper_voice_path(self, persona: PersonaVoiceSettings) -> Path:
        """Get path to Piper voice model for persona using Model Manager."""
        try:
            # Import here to avoid circular dependencies
            from .model_manager import get_piper_voice_path
            
            # Map persona name to model manager format
            persona_name = persona.persona_name.lower().replace(" ", "_")
            
            # Use model manager to get appropriate voice
            # This will download if not available
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                path = loop.run_until_complete(
                    get_piper_voice_path(persona_name, self.data_dir)
                )
                return path
            finally:
                loop.close()
                
        except Exception as e:
            logger.warning(f"Model Manager failed, using fallback: {e}")
            # Fallback to original behavior
            voices_dir = self.data_dir / "models" / "piper"
            voices_dir.mkdir(parents=True, exist_ok=True)
            
            # Select voice based on persona characteristics
            if persona.persona_name == "Grandma Rose":
                return voices_dir / "en_US-ljspeech-high.onnx"
            elif persona.persona_name == "Maya":
                return voices_dir / "en_US-amy-medium.onnx"  
            elif persona.persona_name == "Alex":
                return voices_dir / "en_US-ryan-high.onnx"
            else:
                return voices_dir / "en_US-ljspeech-medium.onnx"  # Default
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current interaction statistics."""
        return self.interaction_stats.copy()


class NixHumanityConversationProcessor(Processor):
    """Pipecat processor that handles conversation with Nix for Humanity."""
    
    def __init__(self, nix_interface: BackendInterface, persona_settings: PersonaVoiceSettings):
        super().__init__()
        self.nix_interface = nix_interface
        self.persona_settings = persona_settings
        self.on_transcript: Optional[Callable[[str], None]] = None
        self.on_response: Optional[Callable[[str], None]] = None
    
    async def process_frame(self, frame):
        """Process incoming frames from the pipeline."""
        if isinstance(frame, TextFrame):
            # This is transcribed speech from the user
            transcript = frame.text
            
            if self.on_transcript:
                self.on_transcript(transcript)
            
            # Process through Nix for Humanity
            try:
                response = await self.nix_interface.process_natural_language(
                    transcript,
                    context=ConversationContext(
                        persona=self.persona_settings.persona_name.lower().replace(" ", "_"),
                        interface_type="voice",
                        conversation_id=f"voice_{datetime.now().isoformat()}"
                    )
                )
                
                # Convert response to speech text
                if hasattr(response, 'display_text'):
                    response_text = response.display_text
                elif hasattr(response, 'message'):
                    response_text = response.message
                else:
                    response_text = str(response)
                
                if self.on_response:
                    self.on_response(response_text)
                
                # Return text frame for TTS
                return TextFrame(response_text)
                
            except Exception as e:
                logger.error(f"Error processing conversation: {e}")
                error_text = f"I'm sorry, I encountered an error: {str(e)}"
                return TextFrame(error_text)
        
        # Pass through other frame types
        return frame


# Mock implementations for development
class MockSTTService:
    """Mock Speech-to-Text service for development."""
    
    async def process_frame(self, frame):
        if isinstance(frame, AudioRawFrame):
            # Mock transcription
            return TextFrame("install firefox please")
        return frame


class MockTTSService:
    """Mock Text-to-Speech service for development."""
    
    async def process_frame(self, frame):
        if isinstance(frame, TextFrame):
            # Mock audio generation
            logger.info(f"🗣️ [MOCK TTS] {frame.text}")
            # Return mock audio frame
            return AudioRawFrame(b"mock_audio_data", sample_rate=16000)
        return frame


class MockConversationProcessor:
    """Mock conversation processor for development."""
    
    def __init__(self, nix_interface):
        self.nix_interface = nix_interface
    
    async def process_frame(self, frame):
        if isinstance(frame, TextFrame):
            # Mock processing
            response_text = f"I understand you want to: {frame.text}"
            return TextFrame(response_text)
        return frame