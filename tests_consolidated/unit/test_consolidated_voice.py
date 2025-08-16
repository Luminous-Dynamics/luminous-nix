"""
Unit tests for the consolidated voice module.

These tests verify voice functionality with mocks,
so they work even without audio hardware.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import asyncio

from luminous_nix.voice.consolidated_voice import (
    ConsolidatedVoice,
    SimpleVoiceInterface,
    VoiceConfig,
    create_voice_interface,
    test_voice_setup,
)


class TestConsolidatedVoice:
    """Test the consolidated voice functionality."""
    
    def test_initialization(self):
        """Test voice interface initializes correctly."""
        config = VoiceConfig()
        voice = ConsolidatedVoice(config)
        
        assert voice.config == config
        assert not voice.is_listening
        assert voice._recognizer is None
        assert voice._tts_engine is None
    
    def test_config_defaults(self):
        """Test default configuration values."""
        config = VoiceConfig()
        
        assert config.enable_wake_word is False
        assert config.wake_word == "hey nix"
        assert config.language == "en-US"
        assert config.speech_rate == 150
        assert config.volume == 0.9
        assert config.use_offline is True
    
    @patch('luminous_nix.voice.consolidated_voice.SR_AVAILABLE', False)
    def test_no_speech_recognition(self):
        """Test behavior when speech recognition not available."""
        voice = ConsolidatedVoice()
        
        assert voice.features["speech_recognition"] is False
        assert voice.listen() is None
    
    @patch('luminous_nix.voice.consolidated_voice.TTS_AVAILABLE', False)
    def test_no_tts(self, capsys):
        """Test fallback when TTS not available."""
        voice = ConsolidatedVoice()
        
        # Should fallback to print
        result = voice.speak("Test message")
        
        assert result is True
        captured = capsys.readouterr()
        assert "Test message" in captured.out
    
    @patch('luminous_nix.voice.consolidated_voice.sr')
    @patch('luminous_nix.voice.consolidated_voice.SR_AVAILABLE', True)
    def test_listen_success(self, mock_sr):
        """Test successful speech recognition."""
        # Setup mocks
        mock_recognizer = Mock()
        mock_microphone = Mock()
        mock_audio = Mock()
        
        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.Microphone.return_value = mock_microphone
        mock_recognizer.listen.return_value = mock_audio
        mock_recognizer.recognize_google.return_value = "test command"
        
        voice = ConsolidatedVoice()
        result = voice.listen()
        
        assert result == "test command"
    
    @patch('luminous_nix.voice.consolidated_voice.sr')
    @patch('luminous_nix.voice.consolidated_voice.SR_AVAILABLE', True)
    def test_listen_timeout(self, mock_sr):
        """Test listen timeout handling."""
        mock_sr.WaitTimeoutError = Exception
        mock_recognizer = Mock()
        mock_recognizer.listen.side_effect = mock_sr.WaitTimeoutError()
        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.Microphone.return_value = Mock()
        
        voice = ConsolidatedVoice()
        result = voice.listen(timeout=0.1)
        
        assert result is None
    
    @patch('luminous_nix.voice.consolidated_voice.pyttsx3')
    @patch('luminous_nix.voice.consolidated_voice.TTS_AVAILABLE', True)
    def test_speak_success(self, mock_pyttsx3):
        """Test successful text-to-speech."""
        mock_engine = Mock()
        mock_pyttsx3.init.return_value = mock_engine
        
        voice = ConsolidatedVoice()
        result = voice.speak("Hello world")
        
        assert result is True
        mock_engine.say.assert_called_once_with("Hello world")
        mock_engine.runAndWait.assert_called_once()
    
    def test_wake_word_configuration(self):
        """Test wake word configuration."""
        config = VoiceConfig(enable_wake_word=True, wake_word="hello nix")
        voice = ConsolidatedVoice(config)
        
        assert voice.config.wake_word == "hello nix"
        
        voice.set_wake_word("hi computer")
        assert voice.config.wake_word == "hi computer"
    
    @patch('luminous_nix.voice.consolidated_voice.pyttsx3')
    @patch('luminous_nix.voice.consolidated_voice.TTS_AVAILABLE', True)
    def test_get_available_voices(self, mock_pyttsx3):
        """Test getting available TTS voices."""
        mock_engine = Mock()
        mock_voice = Mock()
        mock_voice.id = "voice1"
        mock_voice.name = "Test Voice"
        mock_voice.languages = ["en-US"]
        mock_voice.gender = "neutral"
        
        mock_engine.getProperty.return_value = [mock_voice]
        mock_pyttsx3.init.return_value = mock_engine
        
        voice = ConsolidatedVoice()
        voices = voice.get_available_voices()
        
        assert len(voices) == 1
        assert voices[0]["id"] == "voice1"
        assert voices[0]["name"] == "Test Voice"
    
    @pytest.mark.asyncio
    async def test_continuous_listening(self):
        """Test continuous listening mode."""
        voice = ConsolidatedVoice()
        
        # Mock the listen method
        commands = ["command 1", "command 2", None]
        voice.listen = Mock(side_effect=commands)
        
        received = []
        def callback(text):
            received.append(text)
            if len(received) >= 2:
                voice.stop_listening()
        
        # Start listening
        task = asyncio.create_task(
            voice.listen_continuously(callback)
        )
        
        # Wait a bit
        await asyncio.sleep(0.5)
        
        # Should have received commands
        assert "command 1" in received
        assert "command 2" in received
        
        # Cleanup
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


class TestSimpleVoiceInterface:
    """Test the text-based voice interface."""
    
    def test_initialization(self):
        """Test simple interface initialization."""
        voice = SimpleVoiceInterface()
        
        assert not voice.is_listening
        assert voice.config is not None
    
    def test_speak(self, capsys):
        """Test text output for speaking."""
        voice = SimpleVoiceInterface()
        result = voice.speak("Test message")
        
        assert result is True
        captured = capsys.readouterr()
        assert "Test message" in captured.out
        assert "🔊" in captured.out  # Speaker emoji
    
    @patch('builtins.input', return_value="test command")
    def test_listen(self, mock_input):
        """Test text input for listening."""
        voice = SimpleVoiceInterface()
        result = voice.listen()
        
        assert result == "test command"
        mock_input.assert_called_once()
    
    def test_test_methods(self):
        """Test that test methods always succeed."""
        voice = SimpleVoiceInterface()
        
        assert voice.test_microphone() is True
        assert voice.test_speaker() is True


class TestFactoryFunction:
    """Test the voice interface factory."""
    
    @patch('luminous_nix.voice.consolidated_voice.SR_AVAILABLE', True)
    def test_create_with_audio(self):
        """Test creation when audio available."""
        voice = create_voice_interface()
        assert isinstance(voice, ConsolidatedVoice)
    
    @patch('luminous_nix.voice.consolidated_voice.SR_AVAILABLE', False)
    @patch('luminous_nix.voice.consolidated_voice.TTS_AVAILABLE', False)
    def test_create_without_audio(self):
        """Test fallback to simple interface."""
        voice = create_voice_interface()
        assert isinstance(voice, SimpleVoiceInterface)
    
    def test_create_with_config(self):
        """Test creation with custom config."""
        config = VoiceConfig(
            enable_wake_word=True,
            speech_rate=200,
            volume=0.5
        )
        
        voice = create_voice_interface(config)
        assert voice.config == config


class TestDiagnostics:
    """Test diagnostic functions."""
    
    @patch('luminous_nix.voice.consolidated_voice.SR_AVAILABLE', True)
    @patch('luminous_nix.voice.consolidated_voice.TTS_AVAILABLE', True)
    @patch('luminous_nix.voice.consolidated_voice.WHISPER_AVAILABLE', False)
    def test_voice_setup(self, capsys):
        """Test voice setup diagnostics."""
        with patch.object(ConsolidatedVoice, 'test_microphone', return_value=True):
            with patch.object(ConsolidatedVoice, 'test_speaker', return_value=True):
                result = test_voice_setup()
        
        assert result is True
        
        captured = capsys.readouterr()
        assert "Voice Interface Diagnostics" in captured.out
        assert "✅" in captured.out  # Check mark for available features


class TestBackwardCompatibility:
    """Test backward compatibility with old voice modules."""
    
    def test_old_imports(self):
        """Test that old class names still work."""
        from luminous_nix.voice import (
            VoiceInterface,
            SpeechRecognizer,
            SpeechSynthesizer,
        )
        
        # All should point to ConsolidatedVoice
        assert VoiceInterface == ConsolidatedVoice
        assert SpeechRecognizer == ConsolidatedVoice
        assert SpeechSynthesizer == ConsolidatedVoice
    
    def test_module_exports(self):
        """Test that module exports are correct."""
        import luminous_nix.voice as voice_module
        
        assert hasattr(voice_module, 'ConsolidatedVoice')
        assert hasattr(voice_module, 'SimpleVoiceInterface')
        assert hasattr(voice_module, 'VoiceConfig')
        assert hasattr(voice_module, 'create_voice_interface')
        assert hasattr(voice_module, 'test_voice_setup')
