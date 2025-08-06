/**
 * JavaScript/TypeScript Client Example for Nix for Humanity API
 * Works in browser and Node.js environments
 */

class NixForHumanityClient {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
        this.sessionId = null;
    }

    /**
     * Process a natural language query
     * @param {string} query - Natural language query
     * @param {Object} options - Query options
     * @returns {Promise<Object>} API response
     */
    async query(query, options = {}) {
        const response = await fetch(`${this.baseUrl}/api/v1/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query,
                session_id: this.sessionId,
                context: {
                    personality: options.personality || 'friendly',
                    execution_mode: options.executionMode || 'dry_run',
                    collect_feedback: options.collectFeedback !== false,
                    capabilities: options.capabilities || ['text']
                }
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        const data = await response.json();
        
        // Store session ID for future requests
        if (data.session_id && !this.sessionId) {
            this.sessionId = data.session_id;
        }

        return data;
    }

    /**
     * Submit feedback for a query
     * @param {Object} feedback - Feedback data
     * @returns {Promise<Object>} API response
     */
    async submitFeedback(feedback) {
        const response = await fetch(`${this.baseUrl}/api/v1/feedback`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: this.sessionId,
                ...feedback
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        return response.json();
    }

    /**
     * Search for packages
     * @param {string} query - Search query
     * @param {number} limit - Maximum results
     * @returns {Promise<Object>} Search results
     */
    async searchPackages(query, limit = 10) {
        const params = new URLSearchParams({
            q: query,
            limit: limit.toString()
        });

        const response = await fetch(`${this.baseUrl}/api/v1/search?${params}`);

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        return response.json();
    }

    /**
     * Get API capabilities
     * @returns {Promise<Object>} Capabilities info
     */
    async getCapabilities() {
        const response = await fetch(`${this.baseUrl}/api/v1/capabilities`);

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        return response.json();
    }

    /**
     * Get session information
     * @returns {Promise<Object>} Session info
     */
    async getSession() {
        if (!this.sessionId) {
            throw new Error('No active session');
        }

        const response = await fetch(`${this.baseUrl}/api/v1/session/${this.sessionId}`);

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        return response.json();
    }
}

// Example usage
async function example() {
    const client = new NixForHumanityClient();

    try {
        // Get capabilities
        const capabilities = await client.getCapabilities();
        console.log('API Capabilities:', capabilities);

        // Ask a question
        const response = await client.query('How do I install Firefox?', {
            personality: 'friendly',
            executionMode: 'dry_run'
        });

        console.log('Response:', response.response.text);
        console.log('Commands:', response.response.commands);

        // Submit feedback
        await client.submitFeedback({
            query: 'How do I install Firefox?',
            response: response.response.text,
            helpful: true,
            rating: 5
        });

        // Search for packages
        const searchResults = await client.searchPackages('python', 5);
        console.log('Search results:', searchResults);

    } catch (error) {
        console.error('Error:', error);
    }
}

// WebSocket example (if using Socket.IO)
function websocketExample() {
    // Requires socket.io-client library
    const socket = io('http://localhost:5000');

    socket.on('connected', (data) => {
        console.log('Connected with session:', data.session_id);
        
        // Send a query
        socket.emit('query', {
            query: 'How do I update my system?',
            personality: 'minimal'
        });
    });

    socket.on('response', (data) => {
        console.log('Real-time response:', data);
    });

    socket.on('error', (error) => {
        console.error('WebSocket error:', error);
    });
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NixForHumanityClient;
}