#!/usr/bin/env node
/**
 * Voice API Bridge Server
 * ======================
 * 
 * Simple Express server that bridges the frontend to Python voice processing.
 * Handles file uploads and WebSocket connections.
 */

const express = require('express');
const multer = require('multer');
const cors = require('cors');
const path = require('path');
const fs = require('fs').promises;
const { spawn } = require('child_process');
const WebSocket = require('ws');

const app = express();
const PORT = 3030;

// Configure multer for file uploads
const upload = multer({ 
    dest: '/tmp/voice-uploads/',
    limits: {
        fileSize: 10 * 1024 * 1024 // 10MB max
    }
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend/voice-ui')));

// Serve the voice UI
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/voice-ui/index.html'));
});

// Voice processing endpoint
app.post('/api/voice/process', upload.single('audio'), async (req, res) => {
    console.log('Processing voice command...');
    
    if (!req.file) {
        return res.status(400).json({ error: 'No audio file provided' });
    }
    
    try {
        // For now, return mock response
        // In production, this would call the Python backend
        const mockResponses = [
            {
                transcript: "install Firefox",
                response: "I'll help you install Firefox right away. This will take about a minute. You'll find it in your applications menu when it's done.",
                intent: "install_package"
            },
            {
                transcript: "update my computer",
                response: "I'll check for updates and install them for you. Your computer might restart when it's done. This usually takes 5-10 minutes.",
                intent: "update_system"
            },
            {
                transcript: "my internet isn't working",
                response: "Let me help fix your internet connection. I'll check your WiFi settings and try to reconnect. This should just take a moment.",
                intent: "fix_wifi"
            }
        ];
        
        // Pick a random response
        const result = mockResponses[Math.floor(Math.random() * mockResponses.length)];
        
        // Clean up uploaded file
        await fs.unlink(req.file.path);
        
        // Send response
        res.json(result);
        
    } catch (error) {
        console.error('Error processing voice:', error);
        res.status(500).json({ error: 'Failed to process voice command' });
    }
});

// Settings endpoint
app.post('/api/voice/settings', (req, res) => {
    console.log('Updating voice settings:', req.body);
    res.json({ success: true });
});

// WebSocket server for real-time communication
const wss = new WebSocket.Server({ port: 8765 });

wss.on('connection', (ws) => {
    console.log('WebSocket client connected');
    
    // Send welcome message
    ws.send(JSON.stringify({
        type: 'welcome',
        message: 'Connected to voice assistant'
    }));
    
    ws.on('message', async (message) => {
        try {
            const data = JSON.parse(message);
            console.log('Received:', data.type);
            
            // Handle different message types
            switch (data.type) {
                case 'audio':
                    // Process audio data
                    ws.send(JSON.stringify({
                        type: 'status',
                        message: 'Processing your voice command...'
                    }));
                    
                    // Simulate processing
                    setTimeout(() => {
                        ws.send(JSON.stringify({
                            type: 'response',
                            transcript: 'install Firefox',
                            response: "I'll help you install Firefox right away!",
                            intent: 'install_package'
                        }));
                    }, 1500);
                    break;
                    
                case 'text':
                    // Process text command
                    ws.send(JSON.stringify({
                        type: 'response',
                        transcript: data.text,
                        response: `I'll help you with: ${data.text}`,
                        intent: 'unknown'
                    }));
                    break;
                    
                case 'settings':
                    // Update settings
                    ws.send(JSON.stringify({
                        type: 'settings_updated',
                        message: 'Settings updated successfully'
                    }));
                    break;
            }
            
        } catch (error) {
            console.error('WebSocket error:', error);
            ws.send(JSON.stringify({
                type: 'error',
                message: 'Sorry, something went wrong'
            }));
        }
    });
    
    ws.on('close', () => {
        console.log('WebSocket client disconnected');
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Voice API Bridge running on http://localhost:${PORT}`);
    console.log(`WebSocket server running on ws://localhost:8765`);
    console.log('\nTo test the voice interface:');
    console.log(`1. Open http://localhost:${PORT} in your browser`);
    console.log('2. Click the microphone button to start recording');
    console.log('3. Or use the WebSocket connection for real-time communication');
});

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('\nShutting down servers...');
    wss.close(() => {
        process.exit(0);
    });
});