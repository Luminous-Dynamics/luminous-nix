"""
from typing import Dict
Model management for non-LLM AI models

This module handles lazy loading and management of specialized AI models
available through NixOS packages.
"""

import os
from pathlib import Path
from typing import Any


class ModelManager:
    """Lazy-loading model manager for efficient resource usage"""

    def __init__(self):
        """Initialize the model manager"""
        self._models: dict[str, Any] = {}
        self._model_paths = self._find_model_paths()
        self._available_models = self._check_available_models()

    def _find_model_paths(self) -> dict[str, Path]:
        """Find models in NixOS store"""
        # Models are provided by NixOS packages
        # These paths would be determined by the nix environment
        paths = {
            "whisper": Path("/run/current-system/sw/share/whisper/models/"),
            "piper": Path("/run/current-system/sw/share/piper/"),
            "spacy": Path("/run/current-system/sw/lib/python3.11/site-packages/"),
        }

        # Filter out non-existent paths
        return {k: v for k, v in paths.items() if v.exists()}

    def _check_available_models(self) -> dict[str, bool]:
        """Check which models are available"""
        available = {}

        # Check for Whisper
        try:
            import whisper_cpp

            available["whisper"] = True
        except ImportError:
            available["whisper"] = False

        # Check for Piper
        try:
            # Piper might be available as a command
            import subprocess

            result = subprocess.run(["which", "piper"], capture_output=True)
            available["piper"] = result.returncode == 0
        except Exception:
            available["piper"] = False

        # Check for spaCy
        try:
            import spacy

            available["spacy"] = True
        except ImportError:
            available["spacy"] = False

        # Check for sentence transformers
        try:
            from sentence_transformers import SentenceTransformer

            available["embeddings"] = True
        except ImportError:
            available["embeddings"] = False

        # Check for scikit-learn
        try:
            import sklearn

            available["sklearn"] = True
        except ImportError:
            available["sklearn"] = False

        return available

    @property
    def whisper(self):
        """Get Whisper model (lazy load)"""
        if not self._available_models.get("whisper"):
            raise ImportError(
                "Whisper is not available. Install with: nix-env -iA nixpkgs.whisper-cpp"
            )

        if "whisper" not in self._models:
            import whisper_cpp

            # Initialize with a small model by default
            model_path = self._model_paths.get("whisper", Path(".")) / "base.en"
            if model_path.exists():
                self._models["whisper"] = whisper_cpp.Whisper(str(model_path))
            else:
                # Fallback to default initialization
                self._models["whisper"] = whisper_cpp.Whisper()

        return self._models["whisper"]

    @property
    def embeddings(self):
        """Get sentence transformer (lazy load)"""
        if not self._available_models.get("embeddings"):
            raise ImportError(
                "Sentence transformers not available. Install with: nix-env -iA nixpkgs.python311Packages.sentence-transformers"
            )

        if "embeddings" not in self._models:
            from sentence_transformers import SentenceTransformer

            # Use a small, efficient model
            self._models["embeddings"] = SentenceTransformer(
                "all-MiniLM-L6-v2", cache_folder="/tmp/nix-humanity-models"
            )

        return self._models["embeddings"]

    @property
    def spacy_nlp(self):
        """Get spaCy NLP model (lazy load)"""
        if not self._available_models.get("spacy"):
            raise ImportError(
                "spaCy not available. Install with: nix-env -iA nixpkgs.python311Packages.spacy"
            )

        if "spacy" not in self._models:
            import spacy

            try:
                # Try to load small English model
                self._models["spacy"] = spacy.load("en_core_web_sm")
            except OSError:
                # Model not downloaded, create blank English model
                self._models["spacy"] = spacy.blank("en")
                if os.getenv("DEBUG"):
                    print("Warning: spaCy model not found, using blank model")

        return self._models["spacy"]

    @property
    def sklearn_available(self) -> bool:
        """Check if scikit-learn is available"""
        return self._available_models.get("sklearn", False)

    def get_available_models(self) -> dict[str, bool]:
        """Get list of available models"""
        return self._available_models.copy()

    def unload_model(self, model_name: str):
        """Unload a model from memory"""
        if model_name in self._models:
            del self._models[model_name]

    def unload_all(self):
        """Unload all models from memory"""
        self._models.clear()
