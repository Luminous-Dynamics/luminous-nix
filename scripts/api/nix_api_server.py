#!/usr/bin/env python3
"""
REST API Server for Nix for Humanity Headless Core
Provides HTTP endpoints for web, mobile, and remote integrations
"""

import os
import sys
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Flask imports
try:
    from flask import Flask, request, jsonify, Response
    from flask_cors import CORS
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
except ImportError:
    print("Error: Flask dependencies not installed")
    print("Install with: pip install flask flask-cors flask-limiter")
    sys.exit(1)

# Import our headless engine
from core.headless_engine import HeadlessEngine, Context, ExecutionMode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:*", "https://localhost:*"])

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize headless engine
engine = HeadlessEngine()

# Session storage (in-memory for now, use Redis in production)
sessions = {}


class APIError(Exception):
    """Custom API error"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


@app.errorhandler(APIError)
def handle_api_error(error):
    """Handle API errors"""
    response = {
        'error': error.message,
        'status': 'error',
        'timestamp': datetime.utcnow().isoformat()
    }
    return jsonify(response), error.status_code


@app.errorhandler(500)
def handle_internal_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal error: {error}")
    response = {
        'error': 'Internal server error',
        'status': 'error',
        'timestamp': datetime.utcnow().isoformat()
    }
    return jsonify(response), 500


@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    stats = engine.get_stats()
    return jsonify({
        'status': 'healthy',
        'version': '0.8.0',
        'uptime': stats['uptime'],
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/v1/query', methods=['POST'])
@limiter.limit("30 per minute")
def process_query():
    """
    Process a natural language query
    
    POST /api/v1/query
    {
        "query": "How do I install Firefox?",
        "session_id": "optional-session-id",
        "context": {
            "personality": "friendly",
            "execution_mode": "dry_run",
            "collect_feedback": true
        }
    }
    """
    try:
        data = request.get_json()
        if not data:
            raise APIError("No JSON data provided")
        
        query = data.get('query')
        if not query:
            raise APIError("Missing 'query' field")
        
        # Get or create session
        session_id = data.get('session_id', str(uuid.uuid4()))
        if session_id not in sessions:
            sessions[session_id] = {
                'created': datetime.utcnow(),
                'interactions': 0
            }
        
        # Build context
        context_data = data.get('context', {})
        execution_mode_str = context_data.get('execution_mode', 'dry_run')
        
        # Convert string to ExecutionMode enum
        try:
            execution_mode = ExecutionMode(execution_mode_str)
        except ValueError:
            execution_mode = ExecutionMode.DRY_RUN
        
        context = Context(
            session_id=session_id,
            personality=context_data.get('personality', 'friendly'),
            execution_mode=execution_mode,
            collect_feedback=context_data.get('collect_feedback', True),
            capabilities=context_data.get('capabilities', ['text'])
        )
        
        # Process query
        response = engine.process(query, context)
        
        # Update session
        sessions[session_id]['interactions'] += 1
        sessions[session_id]['last_interaction'] = datetime.utcnow()
        
        # Build API response
        api_response = {
            'status': 'success',
            'session_id': session_id,
            'response': response.to_dict(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(api_response)
    
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise APIError(f"Failed to process query: {str(e)}", 500)


@app.route('/api/v1/feedback', methods=['POST'])
@limiter.limit("10 per minute")
def submit_feedback():
    """
    Submit feedback for an interaction
    
    POST /api/v1/feedback
    {
        "session_id": "session-id",
        "query": "original query",
        "response": "system response",
        "helpful": true,
        "improved_response": "optional better response",
        "rating": 5
    }
    """
    try:
        data = request.get_json()
        if not data:
            raise APIError("No JSON data provided")
        
        session_id = data.get('session_id')
        if not session_id:
            raise APIError("Missing 'session_id' field")
        
        # Collect feedback
        success = engine.collect_feedback(session_id, data)
        
        if not success:
            raise APIError("Failed to collect feedback", 500)
        
        return jsonify({
            'status': 'success',
            'message': 'Feedback collected successfully',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Error collecting feedback: {e}")
        raise APIError(f"Failed to collect feedback: {str(e)}", 500)


@app.route('/api/v1/stats', methods=['GET'])
def get_stats():
    """Get engine statistics"""
    try:
        stats = engine.get_stats()
        
        # Add API-specific stats
        stats['api'] = {
            'active_sessions': len(sessions),
            'total_sessions': len(sessions)
        }
        
        return jsonify({
            'status': 'success',
            'stats': stats,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise APIError(f"Failed to get stats: {str(e)}", 500)


@app.route('/api/v1/session/<session_id>', methods=['GET'])
def get_session(session_id: str):
    """Get session information"""
    if session_id not in sessions:
        raise APIError("Session not found", 404)
    
    session = sessions[session_id]
    return jsonify({
        'status': 'success',
        'session': {
            'id': session_id,
            'created': session['created'].isoformat(),
            'interactions': session['interactions'],
            'last_interaction': session.get('last_interaction', session['created']).isoformat()
        },
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/v1/search', methods=['GET'])
@limiter.limit("20 per minute")
def search_packages():
    """
    Search for NixOS packages
    
    GET /api/v1/search?q=firefox&limit=10
    """
    try:
        query = request.args.get('q')
        if not query:
            raise APIError("Missing 'q' parameter")
        
        limit = int(request.args.get('limit', 10))
        if limit > 50:
            limit = 50
        
        # Use the engine to search
        context = Context(capabilities=['text'])
        response = engine.process(f"search for {query}", context)
        
        # Extract package results from response
        # This is a simplified version - real implementation would parse better
        packages = []
        if "search" in response.text:
            # Mock some results for now
            packages = [
                {
                    'name': f'{query}',
                    'version': '1.0.0',
                    'description': f'Package matching {query}'
                },
                {
                    'name': f'{query}-dev',
                    'version': '1.0.0',
                    'description': f'Development files for {query}'
                }
            ][:limit]
        
        return jsonify({
            'status': 'success',
            'query': query,
            'count': len(packages),
            'packages': packages,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Error searching packages: {e}")
        raise APIError(f"Failed to search packages: {str(e)}", 500)


@app.route('/api/v1/capabilities', methods=['GET'])
def get_capabilities():
    """Get API capabilities"""
    return jsonify({
        'status': 'success',
        'capabilities': {
            'version': '0.8.0',
            'features': [
                'natural_language_query',
                'package_search',
                'feedback_collection',
                'session_management',
                'personality_modes',
                'execution_modes'
            ],
            'personalities': [
                'minimal',
                'friendly',
                'encouraging',
                'technical',
                'symbiotic'
            ],
            'execution_modes': [
                'dry_run',
                'safe',
                'full',
                'learning'
            ],
            'rate_limits': {
                'query': '30 per minute',
                'search': '20 per minute',
                'feedback': '10 per minute',
                'default': '50 per hour'
            }
        },
        'timestamp': datetime.utcnow().isoformat()
    })


# WebSocket support (optional)
try:
    from flask_socketio import SocketIO, emit, join_room, leave_room
    
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    @socketio.on('connect')
    def handle_connect():
        """Handle WebSocket connection"""
        session_id = str(uuid.uuid4())
        emit('connected', {'session_id': session_id})
        logger.info(f"WebSocket client connected: {session_id}")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle WebSocket disconnection"""
        logger.info("WebSocket client disconnected")
    
    @socketio.on('query')
    def handle_ws_query(data):
        """Handle WebSocket query"""
        try:
            query = data.get('query')
            if not query:
                emit('error', {'message': 'Missing query'})
                return
            
            # Process query
            context = Context(
                session_id=data.get('session_id', str(uuid.uuid4())),
                personality=data.get('personality', 'friendly'),
                capabilities=['text', 'realtime']
            )
            
            response = engine.process(query, context)
            
            # Emit response
            emit('response', response.to_dict())
        
        except Exception as e:
            logger.error(f"WebSocket query error: {e}")
            emit('error', {'message': str(e)})
    
    WEBSOCKET_ENABLED = True
except ImportError:
    WEBSOCKET_ENABLED = False
    socketio = None


def cleanup_old_sessions():
    """Clean up sessions older than 24 hours"""
    cutoff = datetime.utcnow() - timedelta(hours=24)
    to_remove = []
    
    for session_id, session in sessions.items():
        last_active = session.get('last_interaction', session['created'])
        if last_active < cutoff:
            to_remove.append(session_id)
    
    for session_id in to_remove:
        del sessions[session_id]
    
    if to_remove:
        logger.info(f"Cleaned up {len(to_remove)} old sessions")


if __name__ == '__main__':
    # Configuration
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('API_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting Nix for Humanity API Server")
    logger.info(f"Host: {host}, Port: {port}, Debug: {debug}")
    logger.info(f"WebSocket support: {WEBSOCKET_ENABLED}")
    
    if WEBSOCKET_ENABLED and socketio:
        socketio.run(app, host=host, port=port, debug=debug)
    else:
        app.run(host=host, port=port, debug=debug)