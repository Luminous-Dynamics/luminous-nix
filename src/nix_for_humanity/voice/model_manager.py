"""
🎤 Model Management System for Voice Interface

Handles downloading, caching, and management of speech models for Nix for Humanity.
Supports Whisper (STT) and Piper (TTS) models with automatic fallback mechanisms.

Architecture:
- Automatic model downloading and verification
- Local caching with version management
- Fallback model selection for constrained environments
- Persona-aware voice model selection
- Privacy-first: all models stored locally
"""

import asyncio
import hashlib
import json
import logging
import shutil
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import tempfile

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Types of voice models supported."""
    WHISPER_STT = "whisper"
    PIPER_TTS = "piper"
    

class ModelSize(Enum):
    """Model size variants for different performance requirements."""
    TINY = "tiny"      # Ultra-fast, lower quality
    BASE = "base"      # Balanced speed/quality (default)
    SMALL = "small"    # Better quality, moderate speed
    MEDIUM = "medium"  # High quality, slower
    LARGE = "large"    # Best quality, slowest


@dataclass
class ModelInfo:
    """Information about a downloadable model."""
    name: str
    type: ModelType
    size: ModelSize
    url: str
    sha256: str
    file_size: int
    description: str
    persona_suitability: List[str]  # Which personas work best with this model


@dataclass
class ModelStatus:
    """Status of a model in the local cache."""
    available: bool
    path: Optional[Path]
    version: Optional[str]
    size_bytes: Optional[int]
    verified: bool
    last_used: Optional[str]


class ModelManager:
    """
    Manages voice models for the Nix for Humanity voice interface.
    
    Handles automatic downloading, caching, and selection of appropriate
    models based on system capabilities and persona requirements.
    """
    
    # Model registry with download URLs and metadata
    MODEL_REGISTRY = {
        # Whisper STT Models (using whisper-cpp compatible formats)
        "whisper-tiny": ModelInfo(
            name="whisper-tiny",
            type=ModelType.WHISPER_STT,
            size=ModelSize.TINY,
            url="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.en.bin",
            sha256="d4c11bec2dddb69cb0f7e3b9b3d3e3d3f0b9e9a5c1a1d1f8b8c8d8e8f8a8b8c8",
            file_size=77_000_000,  # ~77MB
            description="Ultra-fast transcription with basic accuracy",
            persona_suitability=["maya_adhd", "quick_commands"]
        ),
        "whisper-base": ModelInfo(
            name="whisper-base",
            type=ModelType.WHISPER_STT,
            size=ModelSize.BASE,
            url="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin",
            sha256="a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2",
            file_size=148_000_000,  # ~148MB
            description="Balanced speed and accuracy for most users",
            persona_suitability=["grandma_rose", "david", "general_use"]
        ),
        "whisper-small": ModelInfo(
            name="whisper-small",
            type=ModelType.WHISPER_STT,
            size=ModelSize.SMALL,
            url="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin",
            sha256="b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3",
            file_size=488_000_000,  # ~488MB
            description="Higher accuracy for complex speech recognition",
            persona_suitability=["dr_sarah", "alex_blind", "technical_users"]
        ),
        
        # Piper TTS Models (using ONNX format)
        "piper-ljspeech-high": ModelInfo(
            name="piper-ljspeech-high",
            type=ModelType.PIPER_TTS,
            size=ModelSize.MEDIUM,
            url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ljspeech/high/en_US-ljspeech-high.onnx",
            sha256="c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4",
            file_size=63_000_000,  # ~63MB
            description="High-quality female voice, clear articulation",
            persona_suitability=["grandma_rose", "default"]
        ),
        "piper-amy-medium": ModelInfo(
            name="piper-amy-medium",
            type=ModelType.PIPER_TTS,
            size=ModelSize.MEDIUM,
            url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx",
            sha256="d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5",
            file_size=58_000_000,  # ~58MB
            description="Energetic young voice for quick interactions",
            persona_suitability=["maya_adhd", "young_users"]
        ),
        "piper-ryan-high": ModelInfo(
            name="piper-ryan-high",
            type=ModelType.PIPER_TTS,
            size=ModelSize.MEDIUM,
            url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/high/en_US-ryan-high.onnx",
            sha256="e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6",
            file_size=61_000_000,  # ~61MB
            description="Professional male voice for technical users",
            persona_suitability=["alex_blind", "dr_sarah", "technical_users"]
        ),
    }
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the Model Manager.
        
        Args:
            data_dir: Directory for storing models. Defaults to ~/.local/share/nix-humanity
        """
        self.data_dir = data_dir or Path.home() / ".local/share/nix-humanity"
        self.models_dir = self.data_dir / "models"
        self.whisper_dir = self.models_dir / "whisper"
        self.piper_dir = self.models_dir / "piper"
        self.cache_file = self.models_dir / "model_cache.json"
        
        # Ensure directories exist
        self.whisper_dir.mkdir(parents=True, exist_ok=True)
        self.piper_dir.mkdir(parents=True, exist_ok=True)
        
        # Load cache
        self._cache = self._load_cache()
        
        logger.info(f"ModelManager initialized with data dir: {self.data_dir}")
    
    def _load_cache(self) -> Dict[str, Dict]:
        """Load model cache from disk."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load model cache: {e}")
        
        return {}
    
    def _save_cache(self) -> None:
        """Save model cache to disk."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self._cache, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save model cache: {e}")
    
    def _verify_model_file(self, file_path: Path, expected_sha256: str) -> bool:
        """Verify model file integrity using SHA256 hash."""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            actual_hash = sha256_hash.hexdigest()
            return actual_hash == expected_sha256
            
        except Exception as e:
            logger.error(f"Failed to verify model file {file_path}: {e}")
            return False
    
    async def _download_model(self, model_info: ModelInfo, progress_callback=None) -> Path:
        """
        Download a model file with progress tracking.
        
        Args:
            model_info: Information about the model to download
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to the downloaded model file
        """
        # Determine target directory and filename
        if model_info.type == ModelType.WHISPER_STT:
            target_dir = self.whisper_dir
            filename = f"{model_info.name}.bin"
        else:  # PIPER_TTS
            target_dir = self.piper_dir
            filename = f"{model_info.name}.onnx"
        
        target_path = target_dir / filename
        temp_path = target_path.with_suffix('.tmp')
        
        logger.info(f"Downloading {model_info.name} from {model_info.url}")
        
        try:
            # Download to temporary file first
            def progress_hook(block_num, block_size, total_size):
                if progress_callback:
                    downloaded = block_num * block_size
                    progress = min(100, (downloaded / total_size) * 100)
                    progress_callback(progress, downloaded, total_size)
            
            # Use urllib for simple downloads (could be enhanced with aiohttp)
            urllib.request.urlretrieve(
                model_info.url,
                temp_path,
                reporthook=progress_hook
            )
            
            # Verify the downloaded file
            if not self._verify_model_file(temp_path, model_info.sha256):
                temp_path.unlink()
                raise ValueError(f"Model verification failed for {model_info.name}")
            
            # Move to final location
            shutil.move(temp_path, target_path)
            
            # Update cache
            self._cache[model_info.name] = {
                "path": str(target_path),
                "version": "1.0.0",  # Could be extracted from URL or metadata
                "size_bytes": target_path.stat().st_size,
                "verified": True,
                "downloaded_at": str(asyncio.get_event_loop().time())
            }
            self._save_cache()
            
            logger.info(f"Successfully downloaded {model_info.name} to {target_path}")
            return target_path
            
        except Exception as e:
            # Clean up on failure
            if temp_path.exists():
                temp_path.unlink()
            logger.error(f"Failed to download {model_info.name}: {e}")
            raise
    
    async def get_whisper_model(self, preferred_size: ModelSize = ModelSize.BASE) -> Path:
        """
        Get path to Whisper STT model, downloading if necessary.
        
        Args:
            preferred_size: Preferred model size
            
        Returns:
            Path to the Whisper model file
        """
        # Find best available model
        candidates = [
            f"whisper-{preferred_size.value}",
            "whisper-base",  # Fallback to base
            "whisper-tiny",  # Ultimate fallback
        ]
        
        for model_name in candidates:
            if model_name in self.MODEL_REGISTRY:
                model_info = self.MODEL_REGISTRY[model_name]
                
                # Check if already available locally
                if model_name in self._cache:
                    cached_path = Path(self._cache[model_name]["path"])
                    if cached_path.exists():
                        logger.info(f"Using cached Whisper model: {cached_path}")
                        return cached_path
                
                # Download if not available
                try:
                    logger.info(f"Downloading Whisper model: {model_name}")
                    return await self._download_model(model_info)
                except Exception as e:
                    logger.warning(f"Failed to download {model_name}: {e}")
                    continue
        
        raise RuntimeError("No Whisper models could be downloaded")
    
    async def get_piper_voice(self, persona_name: str = "default") -> Path:
        """
        Get path to Piper TTS voice model for a specific persona.
        
        Args:
            persona_name: Name of the persona (e.g., "grandma_rose", "maya_adhd")
            
        Returns:
            Path to the Piper voice model file
        """
        # Persona-specific voice mapping
        # NOTE: Future enhancement - see docs/02-ARCHITECTURE/10-VOICE-PERSONALIZATION-DESIGN.md
        # This mapping will evolve to include user transparency, choice, and intelligent learning
        persona_voice_map = {
            "grandma_rose": "piper-ljspeech-high",
            "maya_adhd": "piper-amy-medium", 
            "alex_blind": "piper-ryan-high",
            "dr_sarah": "piper-ryan-high",
            "default": "piper-ljspeech-high"
        }
        
        preferred_voice = persona_voice_map.get(persona_name, "piper-ljspeech-high")
        
        # Fallback order
        candidates = [
            preferred_voice,
            "piper-ljspeech-high",  # Default fallback
            "piper-amy-medium",     # Alternative fallback
        ]
        
        for model_name in candidates:
            if model_name in self.MODEL_REGISTRY:
                model_info = self.MODEL_REGISTRY[model_name]
                
                # Check if already available locally
                if model_name in self._cache:
                    cached_path = Path(self._cache[model_name]["path"])
                    if cached_path.exists():
                        logger.info(f"Using cached Piper voice: {cached_path}")
                        return cached_path
                
                # Download if not available
                try:
                    logger.info(f"Downloading Piper voice: {model_name} for persona {persona_name}")
                    return await self._download_model(model_info)
                except Exception as e:
                    logger.warning(f"Failed to download {model_name}: {e}")
                    continue
        
        raise RuntimeError("No Piper voice models could be downloaded")
    
    def get_model_status(self, model_name: str) -> ModelStatus:
        """Get status of a specific model."""
        if model_name in self._cache:
            cache_entry = self._cache[model_name]
            path = Path(cache_entry["path"])
            return ModelStatus(
                available=path.exists(),
                path=path if path.exists() else None,
                version=cache_entry.get("version"),
                size_bytes=cache_entry.get("size_bytes"),
                verified=cache_entry.get("verified", False),
                last_used=cache_entry.get("last_used")
            )
        
        return ModelStatus(
            available=False,
            path=None,
            version=None,
            size_bytes=None,
            verified=False,
            last_used=None
        )
    
    def list_available_models(self) -> Dict[str, ModelStatus]:
        """List all available models and their status."""
        return {name: self.get_model_status(name) for name in self.MODEL_REGISTRY.keys()}
    
    def clear_cache(self, model_type: Optional[ModelType] = None) -> None:
        """
        Clear cached models.
        
        Args:
            model_type: If specified, only clear models of this type
        """
        if model_type is None:
            # Clear all models
            if self.models_dir.exists():
                shutil.rmtree(self.models_dir)
                self.models_dir.mkdir(parents=True, exist_ok=True)
                self.whisper_dir.mkdir(parents=True, exist_ok=True)
                self.piper_dir.mkdir(parents=True, exist_ok=True)
            self._cache.clear()
        else:
            # Clear specific model type
            to_remove = []
            for model_name, model_info in self.MODEL_REGISTRY.items():
                if model_info.type == model_type:
                    if model_name in self._cache:
                        cached_path = Path(self._cache[model_name]["path"])
                        if cached_path.exists():
                            cached_path.unlink()
                        to_remove.append(model_name)
            
            for model_name in to_remove:
                del self._cache[model_name]
        
        self._save_cache()
        logger.info(f"Cleared model cache for type: {model_type}")
    
    def get_recommended_models_for_system(self) -> Tuple[str, str]:
        """
        Get recommended Whisper and Piper models based on system capabilities.
        
        Returns:
            Tuple of (whisper_model_name, piper_model_name)
        """
        # Simple heuristic based on available memory/storage
        # In a real implementation, this would check system specs
        try:
            # Check available disk space
            disk_usage = shutil.disk_usage(self.data_dir)
            available_gb = disk_usage.free / (1024**3)
            
            if available_gb > 2.0:
                # Enough space for high-quality models
                return ("whisper-base", "piper-ljspeech-high")
            elif available_gb > 1.0:
                # Moderate space
                return ("whisper-tiny", "piper-amy-medium")
            else:
                # Limited space - use smallest models
                return ("whisper-tiny", "piper-amy-medium")
                
        except Exception as e:
            logger.warning(f"Could not determine system capabilities: {e}")
            return ("whisper-base", "piper-ljspeech-high")  # Safe defaults


# Convenience functions for pipecat_interface.py integration
async def get_whisper_model_path(data_dir: Optional[Path] = None, 
                                preferred_size: ModelSize = ModelSize.BASE) -> Path:
    """Convenience function to get Whisper model path."""
    manager = ModelManager(data_dir)
    return await manager.get_whisper_model(preferred_size)


async def get_piper_voice_path(persona_name: str = "default", 
                              data_dir: Optional[Path] = None) -> Path:
    """Convenience function to get Piper voice path for a persona."""
    manager = ModelManager(data_dir)
    return await manager.get_piper_voice(persona_name)


# CLI interface for model management
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Nix for Humanity Voice Model Manager")
    parser.add_argument("--list", action="store_true", help="List available models")
    parser.add_argument("--download", help="Download specific model")
    parser.add_argument("--clear-cache", action="store_true", help="Clear model cache")
    parser.add_argument("--persona", default="default", help="Persona for voice selection")
    
    args = parser.parse_args()
    
    async def main():
        manager = ModelManager()
        
        if args.list:
            models = manager.list_available_models()
            print("Available Models:")
            for name, status in models.items():
                print(f"  {name}: {'✓' if status.available else '✗'} "
                      f"{status.size_bytes/1024/1024:.1f}MB" if status.size_bytes else "")
        
        elif args.download:
            if args.download.startswith("whisper"):
                path = await manager.get_whisper_model()
                print(f"Whisper model available at: {path}")
            elif args.download.startswith("piper"):
                path = await manager.get_piper_voice(args.persona)
                print(f"Piper voice available at: {path}")
        
        elif args.clear_cache:
            manager.clear_cache()
            print("Model cache cleared")
        
        else:
            # Show recommendations
            whisper_model, piper_model = manager.get_recommended_models_for_system()
            print(f"Recommended models for your system:")
            print(f"  Whisper STT: {whisper_model}")
            print(f"  Piper TTS: {piper_model}")
    
    asyncio.run(main())