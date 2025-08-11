#!/usr/bin/env python3
"""
🌐 Run the Nix for Humanity REST API Server

This starts the FastAPI server that provides REST endpoints
for all Nix for Humanity operations.
"""

import sys
from pathlib import Path

import uvicorn

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nix_for_humanity.api.v1 import app

if __name__ == "__main__":
    print(
        """
╔══════════════════════════════════════════════════════════╗
║  🌐 Nix for Humanity API Server v1.0                      ║
║  ──────────────────────────────────────────────────────  ║
║  Natural language NixOS through REST API                  ║
║                                                            ║
║  Endpoints:                                                ║
║    POST   /api/v1/execute         - Run any command       ║
║    POST   /api/v1/generate-config - Generate configs      ║
║    POST   /api/v1/search          - Smart search          ║
║    WS     /api/v1/stream          - Real-time updates     ║
║    GET    /api/v1/health          - Health check          ║
║                                                            ║
║  Documentation:                                            ║
║    http://localhost:8080/api/docs - Interactive docs      ║
║    http://localhost:8080/api/redoc - ReDoc interface      ║
║                                                            ║
║  Press Ctrl+C to stop the server                          ║
╚══════════════════════════════════════════════════════════╝
    """
    )

    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info",
        access_log=True,
        reload=False,  # Set to True for development
    )
